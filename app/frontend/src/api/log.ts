import { innerAPI, type Logs } from "./api";

export default class LogsController {
  writeLog(logs: Logs) {
    if (innerAPI.logs) innerAPI.logs.write_log(logs);
    console.log("writeLog", logs);
  }
}
