const { contextBridge } = require("electron")


contextBridge.exposeInMainWorld("poa", {
  platform: process.platform
})
