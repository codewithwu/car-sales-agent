"""图节点和条件边函数模块."""

from typing import Literal

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_agent.agents.base import get_singleton_client

from src.agents.rule_engine import engine
from src.agents.state import State
from src.agents.tools import get_dataframe

# 系统提示词配置
SYSTEM_PROMPT = """
你是一个汽车销售数据分析助手，可以帮助用户查询和分析汽车销售数据。

## 可查询的字段
- 日期：销售日期
- 品牌：汽车品牌（丰田、本田、福特、雪佛兰、日产、宝马、奔驰、奥迪、现代、起亚）
- 车型：汽车类型（轿车、SUV、卡车、两厢车、跑车、厢式车）
- 颜色：车身颜色（红色、蓝色、黑色、白色、银色、灰色、绿色）
- 年份：出厂年份（2015-2022）
- 价格：成交价格（元）
- 里程：行驶里程（公里）
- 排量：发动机排量（L）
- 油耗：百公里油耗（L）
- 销售员：销售人员（张三、李四、王五、赵六、孙七）

## 示例问题
- "查询丰田轿车的价格"
- "红色SUV有哪些？"
- "张三卖得最好的车是什么品牌？"
- "价格在5万到8万之间的有哪些？"
"""

SYSTEM_PROMPT_TOOL = """
你是一个汽车销售数据分析助手，可以帮助用户查询和分析汽车销售数据。

## 可查询的字段
- 日期：销售日期
- 日期：销售日期
- 品牌：汽车品牌（丰田、本田、福特、雪佛兰、日产、宝马、奔驰、奥迪、现代、起亚）
- 车型：汽车类型（轿车、SUV、卡车、两厢车、跑车、厢式车）
- 颜色：车身颜色（红色、蓝色、黑色、白色、银色、灰色、绿色）
- 年份：出厂年份（2015-2022）
- 价格：成交价格（元）
- 里程：行驶里程（公里）
- 排量：发动机排量（L）
- 油耗：百公里油耗（L）
- 销售员：销售人员（张三、李四、王五、赵六、孙七）

## 可用工具
1. query_car_data: 根据多条件查询汽车销售数据
   - brand: 品牌名称
   - model: 车型
   - color: 颜色
   - sales_person: 销售员
   - min_price: 最低价格
   - max_price: 最高价格
   - limit: 返回记录数

## 示例问题
- "查询丰田轿车的价格"
- "红色SUV有哪些？"
- "张三卖得最好的车是什么品牌？"
- "价格在5万到8万之间的有哪些？"

每次只调用一个工具，解决用户的问题。
"""

basic_model = get_singleton_client(llm_provider="longcat")


def rule_based_query_node(state: State) -> dict:
    """基于规则引擎的智能查询节点.

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    messages = state["messages"]
    query = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), None
    )
    if not query:
        return {"messages": [AIMessage("用户输入内容为空")], "is_true": False}

    df = get_dataframe()
    if df is None:
        return {"messages": [AIMessage("数据未初始化")], "is_true": False}

    query_text = query if isinstance(query, str) else str(query)
    intent, params = engine.match(query_text)
    params["limit"] = 10

    if intent is None:
        return {
            "messages": [
                AIMessage("无法理解您的查询，请尝试：查询丰田轿车、红色SUV等")
            ],
            "is_true": False,
        }

    if intent == "query_car":
        return {"messages": [AIMessage(engine._query_car(df, params))], "is_true": True}
    elif intent == "query_salesperson":
        return {
            "messages": [AIMessage(engine._query_by_salesperson(df))],
            "is_true": True,
        }

    return {"messages": [AIMessage("未知意图")], "is_true": False}


def call_llm(state: State) -> dict:
    """调用 LLM 生成回复.

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    messages = state["messages"]
    messages_with_system = [SystemMessage(SYSTEM_PROMPT)] + messages
    ai_message = basic_model.invoke(messages_with_system)

    return {"messages": [ai_message]}


def false_message(state: State) -> dict:
    """无法回答时的回复节点.

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    return {"messages": [AIMessage("暂时无法回答您的问题。")]}


def call_llm_tool(state: State) -> dict:
    """调用带工具的 LLM.

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    from src.agents.tools import query_car_data

    messages = state["messages"]
    query = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), None
    )

    messages_for_llm = [SystemMessage(SYSTEM_PROMPT_TOOL), HumanMessage(query)]
    basic_model_tools = basic_model.bind_tools([query_car_data])

    response = basic_model_tools.invoke(messages_for_llm)

    tool_messages = []
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_message = query_car_data.invoke(tool_call)
            tool_messages.append(tool_message)
        return {"messages": tool_messages, "is_true": True}

    return {"is_true": False}


def check_punchline(state: State) -> Literal["Fail", "Pass"]:
    """条件边函数 - 检查规则引擎是否成功匹配.

    Args:
        state: 当前状态

    Returns:
        "Pass" 如果 is_true 为 True，否则 "Fail"
    """
    if state["is_true"]:
        return "Pass"
    return "Fail"


def check_punchline_tool(state: State) -> Literal["Fail", "Pass"]:
    """条件边函数 - 检查工具调用是否成功.

    Args:
        state: 当前状态

    Returns:
        "Pass" 如果 is_true 为 True，否则 "Fail"
    """
    if state["is_true"]:
        return "Pass"
    return "Fail"
