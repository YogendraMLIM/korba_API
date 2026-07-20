module.exports = {
  apps: [
    {
      name: "korba-api",
      script: "uvicorn",
      args: "app:app --host 0.0.0.0 --port 5509",
      interpreter: "C:/inetpub/PM2-APIs/korba_FastAPI/py-env/Scripts/pythonw.exe",
      cwd: "C:/inetpub/PM2-APIs/korba_FastAPI",
      autorestart: true,
      watch: false
    }
  ]
}
