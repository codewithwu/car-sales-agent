"""FastAPI 应用 - 汽车销售数据分析接口."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

from src.agents import graph, load_sample_data
from langchain.messages import HumanMessage
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 启动时初始化数据."""
    load_sample_data()
    yield


app = FastAPI(title="汽车销售数据分析 API", lifespan=lifespan)


class QueryRequest(BaseModel):
    """查询请求."""

    query: str


class QueryResponse(BaseModel):
    """查询响应."""

    answer: str


@app.get("/", response_class=HTMLResponse)
async def index():
    """返回聊天页面."""
    template_path = os.path.join(
        os.path.dirname(__file__), "..", "templates", "index.html"
    )
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """处理用户查询（非流式）.

    Args:
        request: 查询请求，包含用户问题

    Returns:
        查询响应，包含 AI 回复
    """
    result = graph.invoke({"messages": [HumanMessage(request.query)]})
    answer = result["messages"][-1].content
    return QueryResponse(answer=answer)


@app.post("/stream")
async def stream_query(request: QueryRequest):
    """流式处理用户查询.

    Args:
        request: 查询请求，包含用户问题

    Returns:
        SSE 流式响应
    """

    async def event_generator():
        for chunk in graph.stream(
            {"messages": [HumanMessage(request.query)]},
            stream_mode="messages",
            version="v2",
        ):
            if chunk["type"] == "messages":
                msg, metadata = chunk["data"]
                if msg.content:
                    yield {
                        "event": "message",
                        "data": msg.content,
                    }

        # 发送结束信号
        yield {"event": "end", "data": ""}

    return EventSourceResponse(event_generator())
