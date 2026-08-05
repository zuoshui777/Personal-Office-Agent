const { app, BrowserWindow } = require("electron")
const path = require("path")


const isDev = Boolean(process.env.VITE_DEV_SERVER_URL)


function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, "preload.cjs")
    }
  })

  if (isDev) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL)
  } else {
    // 使用 app.getAppPath() 获取应用根目录，更可靠
    const appPath = app.getAppPath()
    win.loadFile(path.join(appPath, "dist/index.html"))
  }
}


app.whenReady().then(() => {
  createWindow()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})


app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit()
  }
})
