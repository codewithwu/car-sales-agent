"""规则引擎模块 - 用于意图识别和参数提取."""

import re
from typing import Optional

BRANDS = [
    "丰田",
    "本田",
    "福特",
    "雪佛兰",
    "日产",
    "宝马",
    "奔驰",
    "奥迪",
    "现代",
    "起亚",
]
MODELS = ["轿车", "SUV", "卡车", "两厢车", "跑车", "厢式车"]
COLORS = ["红色", "蓝色", "黑色", "白色", "银色", "灰色", "绿色"]
SALES_PERSONS = ["张三", "李四", "王五", "赵六", "孙七"]


class RuleEngine:
    """快速规则匹配引擎，用于意图识别和参数提取."""

    def __init__(self) -> None:
        self.brands = BRANDS
        self.models = MODELS
        self.colors = COLORS
        self.sales_persons = SALES_PERSONS

    def match(self, query: str) -> tuple[Optional[str], dict]:
        """匹配用户输入，返回 (意图, 参数).

        Args:
            query: 用户查询字符串

        Returns:
            元组 (意图, 参数字典)
        """
        query = query.strip()

        params = {}
        intent = "query_car"

        # 1. 提取价格区间
        price_params = self._extract_price(query)
        params.update(price_params)

        # 2. 提取品牌
        for brand in self.brands:
            if brand in query:
                params["brand"] = brand
                break

        # 3. 提取车型
        for model in self.models:
            if model in query:
                params["model"] = model
                break

        # 4. 提取颜色
        for color in self.colors:
            if color in query:
                params["color"] = color
                break

        # 5. 提取销售员
        for sp in self.sales_persons:
            if sp in query:
                params["sales_person"] = sp
                break

        # 判断是否有查询意图
        if any(
            k in params
            for k in [
                "brand",
                "model",
                "color",
                "sales_person",
                "min_price",
                "max_price",
            ]
        ):
            return intent, params

        # 6. 检查销售员统计
        if any(word in query for word in ["销售员", "谁卖", "业绩", "排名"]):
            return "query_salesperson", {}

        return None, {}

    def _extract_price(self, query: str) -> dict:
        """提取价格区间参数.

        Args:
            query: 用户查询字符串

        Returns:
            包含价格参数的字典
        """
        params = {}

        # 匹配 "价格XX至YY" 或 "价格XX到YY"
        m = re.search(r"价格\s*(\d+(?:\.\d+)?)\s*(?:至|到)\s*(\d+(?:\.\d+)?)", query)
        if m:
            params["min_price"] = float(m.group(1))
            params["max_price"] = float(m.group(2))
            return params

        # 匹配 "不超过XX万" 或 "XX万以下"
        m = re.search(r"(?:不超过|低于|以下)\s*(\d+(?:\.\d+)?)\s*万", query)
        if m:
            params["max_price"] = float(m.group(1)) * 10000
            return params

        # 匹配 "不低于XX万" 或 "XX万以上"
        m = re.search(r"(?:不低于|高于|以上)\s*(\d+(?:\.\d+)?)\s*万", query)
        if m:
            params["min_price"] = float(m.group(1)) * 10000
            return params

        return params

    def _query_car(self, df, params: dict) -> str:
        """查询车辆数据.

        Args:
            df: 车辆数据 DataFrame
            params: 查询参数

        Returns:
            查询结果字符串
        """
        result = df.copy()

        if "brand" in params:
            result = result[result["品牌"] == params["brand"]]
        if "model" in params:
            result = result[result["车型"] == params["model"]]
        if "color" in params:
            result = result[result["颜色"] == params["color"]]
        if "sales_person" in params:
            result = result[result["销售员"] == params["sales_person"]]
        if "min_price" in params:
            result = result[result["价格"] >= params["min_price"]]
        if "max_price" in params:
            result = result[result["价格"] <= params["max_price"]]

        if result.empty:
            return "未找到匹配的数据"

        limit = params.get("limit", 10)
        result = result.head(limit)

        return f"找到 {len(result)} 条记录：\n{result.to_string(index=False)}"

    def _query_by_salesperson(self, df) -> str:
        """按销售员统计.

        Args:
            df: 车辆数据 DataFrame

        Returns:
            销售员统计结果字符串
        """
        sp_stats = df.groupby("销售员").agg({"价格": ["count", "sum", "mean"]}).round(2)
        sp_stats.columns = ["销量", "总销售额", "平均单价"]
        sp_stats = sp_stats.sort_values("总销售额", ascending=False)

        return f"销售员业绩排名：\n{sp_stats.to_string()}"

    def build_response(self, query: str, df) -> str:
        """根据规则匹配结果构建响应.

        Args:
            query: 用户查询
            df: 车辆数据 DataFrame

        Returns:
            响应字符串
        """
        intent, params = self.match(query)

        if intent is None:
            return "无法理解您的查询，请尝试：查询丰田轿车、红色SUV等"

        if intent == "query_car":
            return self._query_car(df, params)
        elif intent == "query_salesperson":
            return self._query_by_salesperson(df)

        return "未知意图"


# 全局规则引擎实例
engine = RuleEngine()
