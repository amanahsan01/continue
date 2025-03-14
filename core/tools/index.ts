import { createNewFileTool } from "./definitions/createNewFile";
import { editFileTool } from "./definitions/editFile";
import { exactSearchTool } from "./definitions/exactSearch";
import { readCurrentlyOpenFileTool } from "./definitions/readCurrentlyOpenFile";
import { readFileTool } from "./definitions/readFile";
import { runTerminalCommandTool } from "./definitions/runTerminalCommand";
import { searchWebTool } from "./definitions/searchWeb";
import { viewDiffTool } from "./definitions/viewDiff";
import { viewRepoMapTool } from "./definitions/viewRepoMap";
import { viewSubdirectoryTool } from "./definitions/viewSubdirectory";

export const allTools = [
  readFileTool,
  editFileTool,
  createNewFileTool,
  runTerminalCommandTool,
  viewSubdirectoryTool,
  viewRepoMapTool,
  exactSearchTool,
  searchWebTool,
  viewDiffTool,
  readCurrentlyOpenFileTool,
];
