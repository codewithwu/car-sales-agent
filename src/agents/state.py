"""状态定义模块."""

from typing import Optional

from langgraph.graph import MessagesState


class State(MessagesState):
    """代理状态，包含消息历史和条件路由标志."""

    is_true: Optional[bool] = None
