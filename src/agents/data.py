"""模拟数据生成模块 - 带缓存的汽车销售数据."""

from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional

import numpy as np
import pandas as pd

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

# 全局数据缓存
_df_cache: Optional[pd.DataFrame] = None


@lru_cache()
def generate_sales_data(n_rows: int = 1000, seed: Optional[int] = None) -> pd.DataFrame:
    """生成汽车销售模拟数据.

    Args:
        n_rows: 数据行数，默认 1000
        seed: 随机种子，默认 None（每次不同）

    Returns:
        汽车销售 DataFrame
    """
    if seed is not None:
        np.random.seed(seed)

    start_date = datetime(2022, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_rows)]

    data = {
        "日期": dates,
        "品牌": np.random.choice(BRANDS, n_rows),
        "车型": np.random.choice(MODELS, n_rows),
        "颜色": np.random.choice(COLORS, n_rows),
        "年份": np.random.randint(2015, 2023, n_rows),
        "价格": np.random.uniform(20000, 80000, n_rows).round(2),
        "里程": np.random.uniform(0, 100000, n_rows).round(0),
        "排量": np.random.choice([1.6, 2.0, 2.5, 3.0, 3.5, 4.0], n_rows),
        "油耗": np.random.uniform(20, 40, n_rows).round(1),
        "销售员": np.random.choice(SALES_PERSONS, n_rows),
    }

    df = pd.DataFrame(data).sort_values("日期").reset_index(drop=True)
    return df


def get_dataframe() -> Optional[pd.DataFrame]:
    """获取缓存的数据 DataFrame.

    Returns:
        缓存的 DataFrame 或 None
    """
    return _df_cache


def set_dataframe(df: pd.DataFrame) -> None:
    """设置全局 DataFrame 供工具使用.

    Args:
        df: 车辆数据 DataFrame
    """
    global _df_cache
    _df_cache = df


def load_sample_data(n_rows: int = 1000, seed: Optional[int] = None) -> pd.DataFrame:
    """加载示例数据（生成并缓存）.

    Args:
        n_rows: 数据行数
        seed: 随机种子

    Returns:
        汽车销售 DataFrame
    """
    df = generate_sales_data(n_rows=n_rows, seed=seed)
    set_dataframe(df)
    return df
