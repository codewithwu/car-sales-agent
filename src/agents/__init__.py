"""agents 模块 - 汽车销售数据分析代理.

提供基于规则引擎和 LangGraph 的汽车销售数据分析功能。

Example:
    >>> from src.agents import graph, load_sample_data
    >>> from langchain.messages import HumanMessage
    >>>
    >>> # 加载示例数据
    >>> load_sample_data()
    >>>
    >>> # 调用代理
    >>> graph.invoke({"messages": [HumanMessage("丰田轿车有哪些？")]})
"""

from src.agents.data import (
    load_sample_data,
    get_dataframe,
    set_dataframe,
    generate_sales_data,
)
from src.agents.graph import graph
from src.agents.rule_engine import RuleEngine, engine
from src.agents.state import State
from src.agents.tools import query_car_data, rule_based_query

__all__ = [
    "graph",
    "State",
    "RuleEngine",
    "engine",
    "rule_based_query",
    "query_car_data",
    "set_dataframe",
    "get_dataframe",
    "load_sample_data",
    "generate_sales_data",
]
