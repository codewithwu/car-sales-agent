"""工具函数模块 - LangChain tools."""

from typing import Annotated, Optional

from langchain.tools import tool

from src.agents.rule_engine import engine
from src.agents.data import get_dataframe, set_dataframe

__all__ = ["rule_based_query", "query_car_data", "set_dataframe", "get_dataframe"]


@tool
def rule_based_query(query: str, limit: int = 10) -> str:
    """基于规则引擎的智能查询工具.

    自动从用户输入中识别查询意图和参数，无需手动指定。

    Args:
        query: 自然语言查询（如："丰田轿车"、"红色SUV"、"价格在5万至8万"）
        limit: 返回的最大记录数，默认为 10

    Returns:
        查询结果字符串
    """
    df = get_dataframe()
    if df is None:
        return "数据未初始化"

    intent, params = engine.match(query)
    params["limit"] = limit

    if intent is None:
        return "无法理解您的查询，请尝试：查询丰田轿车、红色SUV等"

    if intent == "query_car":
        return engine._query_car(df, params)
    elif intent == "query_salesperson":
        return engine._query_by_salesperson(df)

    return "未知意图"


@tool
def query_car_data(
    brand: Annotated[Optional[str], "品牌名称"] = None,
    model: Annotated[Optional[str], "车型"] = None,
    color: Annotated[Optional[str], "颜色"] = None,
    sales_person: Annotated[Optional[str], "销售员"] = None,
    min_price: Annotated[Optional[float], "最低价格"] = None,
    max_price: Annotated[Optional[float], "最高价格"] = None,
    limit: Annotated[int, "返回的最大记录数"] = 10,
) -> str:
    """查询汽车销售数据.

    根据条件筛选数据并返回结果，支持多条件组合。

    Args:
        brand: 品牌名称（如：丰田、本田、宝马）
        model: 车型（如：轿车、SUV、卡车）
        color: 颜色（如：红色、蓝色、黑色）
        sales_person: 销售员（如：张三、李四）
        min_price: 最低价格（元）
        max_price: 最高价格（元）
        limit: 返回的最大记录数，默认为 10

    Returns:
        查询结果字符串
    """
    df = get_dataframe()
    if df is None:
        return "数据未初始化"

    result = df.copy()

    if brand:
        result = result[result["品牌"] == brand]
    if model:
        result = result[result["车型"] == model]
    if color:
        result = result[result["颜色"] == color]
    if sales_person:
        result = result[result["销售员"] == sales_person]
    if min_price is not None:
        result = result[result["价格"] >= min_price]
    if max_price is not None:
        result = result[result["价格"] <= max_price]

    result = result.head(limit)

    if result.empty:
        return "未找到匹配的数据"

    return f"找到 {len(result)} 条记录：\n{result.to_string(index=False)}"
