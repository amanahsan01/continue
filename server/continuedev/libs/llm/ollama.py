import json
from typing import Any, Callable, Dict, Optional

from pydantic import Field, validator

from ...core.main import ContinueCustomException
from ..util.logging import logger
from .base import LLM, CompletionOptions


class Ollama(LLM):
    """
    [Ollama](https://ollama.ai/) is an application for Mac and Linux that makes it easy to locally run open-source models, including Llama-2. Download the app from the website, and it will walk you through setup in a couple of minutes. You can also read more in their [README](https://github.com/jmorganca/ollama). Continue can then be configured to use the `Ollama` LLM class:

    ```python title="~/.continue/config.py"
    from continuedev.libs.llm.ollama import Ollama

    config = ContinueConfig(
        ...
        models=Models(
            default=Ollama(model="llama2")
        )
    )
    ```
    """

    model: str = "llama2"
    api_base: Optional[str] = Field(
        "http://localhost:11434", description="URL of the Ollama server"
    )

    @validator("api_base", pre=True, always=True)
    def set_api_base(cls, api_base):
        return api_base or "http://localhost:11434"

    class Config:
        arbitrary_types_allowed = True

    def collect_args(self, options: CompletionOptions) -> Dict[str, Any]:
        return {
            "temperature": options.temperature,
            "top_p": options.top_p,
            "top_k": options.top_k,
            "num_predict": options.max_tokens,
            "stop": options.stop,
        }

    async def start(self, *args, **kwargs):
        await super().start(*args, **kwargs)
        try:
            async with self.create_client_session() as session:
                async with session.post(
                    f"{self.api_base}/api/generate",
                    proxy=self.request_options.proxy,
                    json={
                        "prompt": "",
                        "model": self.model,
                    },
                ) as _:
                    pass
        except Exception as e:
            logger.warning(f"Error pre-loading Ollama model: {e}")

    async def get_downloaded_models(self):
        async with self.create_client_session() as session:
            async with session.get(
                f"{self.api_base}/api/tags",
                proxy=self.request_options.proxy,
            ) as resp:
                js_data = await resp.json()
                return list(map(lambda x: x["name"], js_data["models"]))

    async def _stream_complete(self, prompt, options):
        async with self.create_client_session() as session:
            async with session.post(
                f"{self.api_base}/api/generate",
                json={
                    "template": prompt,
                    "model": self.model,
                    "system": self.system_message,
                    "options": self.collect_args(options),
                },
                proxy=self.request_options.proxy,
            ) as resp:
                if resp.status == 400:
                    txt = await resp.text()
                    extra_msg = ""
                    if "no such file" in txt:
                        extra_msg = f"\n\nThis means that the model '{self.model}' is not downloaded.\n\nYou have the following models downloaded: {', '.join(await self.get_downloaded_models())}.\n\nTo download this model, run `ollama run {self.model}` in your terminal."
                    raise ContinueCustomException(
                        f"Ollama returned an error: {txt}{extra_msg}",
                        "Invalid request to Ollama",
                    )
                elif resp.status == 404:
                    raise ContinueCustomException(
                        f"Ollama not found. Please make sure the server is running.\n\n{await resp.text()}",
                        "Ollama not found. Please make sure the server is running.",
                    )
                elif resp.status != 200:
                    raise ContinueCustomException(
                        f"Ollama returned an error: {await resp.text()}",
                        "Invalid request to Ollama",
                    )
                async for line in resp.content.iter_any():
                    if line:
                        json_chunk = line.decode("utf-8")
                        chunks = json_chunk.split("\n")
                        for chunk in chunks:
                            if chunk.strip() != "":
                                try:
                                    j = json.loads(chunk)
                                except Exception as e:
                                    logger.warning(
                                        f"Error parsing Ollama response: {e} {chunk}"
                                    )
                                    continue
                                if "response" in j:
                                    yield j["response"]
