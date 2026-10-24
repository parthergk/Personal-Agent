module.exports = {
  apps: [
    {
      name: "agent-api",
      cwd: "./api",
      script: "./venv/bin/uvicorn",
      args: "main:app --host 127.0.0.1 --port 8000 --workers 2",
      interpreter: "none",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "agent-whatsapp",
      cwd: "./whatsapp",
      script: "dist/index.js",
      interpreter: "node",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        NODE_ENV: "production"
      }
    }
  ]
};
