import { ProfileDescription } from "../config/ConfigHandler.js";

import { ToCoreFromIdeOrWebviewProtocol } from "./core.js";
import { ToWebviewFromIdeOrCoreProtocol } from "./webview.js";

export type ToCoreFromWebviewProtocol = ToCoreFromIdeOrWebviewProtocol & {
  didChangeSelectedProfile: [{ id: string | null }, void];
  didChangeSelectedOrg: [
    { id: string | null; profileId?: string | null },
    void,
  ];
};
export type ToWebviewFromCoreProtocol = ToWebviewFromIdeOrCoreProtocol & {
  didChangeAvailableProfiles: [
    { profiles: ProfileDescription[]; selectedProfileId: string | null },
    void,
  ];
  toolCallPartialOutput: [
    { toolCallId: string; contextItems: any[] },
    void,
  ];
};
