"""LangGraph StateGraph 构建和编译模块."""

from langgraph.graph import END, START, StateGraph

from src.agents.nodes import (
    call_llm,
    call_llm_tool,
    check_punchline,
    check_punchline_tool,
    false_message,
    rule_based_query_node,
)
from src.agents.state import State

# 构建图
builder = StateGraph(State)
builder.add_node("rule_based_query_node", rule_based_query_node)
builder.add_node("false_message", false_message)
builder.add_node("call_llm", call_llm)
builder.add_node("call_llm_tool", call_llm_tool)

builder.add_edge(START, "rule_based_query_node")
builder.add_conditional_edges(
    "rule_based_query_node",
    check_punchline,
    {"Fail": "call_llm_tool", "Pass": "call_llm"},
)
builder.add_conditional_edges(
    "call_llm_tool",
    check_punchline_tool,
    {"Fail": "false_message", "Pass": "call_llm"},
)

builder.add_edge("false_message", END)
builder.add_edge("call_llm", END)

graph = builder.compile()
