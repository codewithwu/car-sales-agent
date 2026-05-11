"""应用入口 - 启动 FastAPI 服务."""

import uvicorn

from src.api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
