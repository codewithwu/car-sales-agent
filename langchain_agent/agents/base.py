"""Agent 基础模块."""

import os
from functools import lru_cache
from typing import Annotated, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

_OPENAI_PROVIDERS = {
    "zhipu": ("智谱", "ZHIPU"),
    "bailing": ("百灵", "LING"),
    "siliconflow": ("硅基流动", "SILICONFLOW"),
    "modelscope": ("魔塔社区", "MODELSCOPE"),
    "longcat": ("美团LongCat", "LONGCAT"),
    "deepseek": ("DeepSeek", "DEEPSEEK"),
}


@lru_cache()
def get_singleton_client(
    llm_provider: Annotated[
        str, "LLM 提供者: 'ollama'、'openai' 或 'bailing'"
    ] = "bailing",
) -> Any:
    """获取 LLM 实例（单例）.

    Args:
        llm_provider: LLM 提供者

    Returns:
        LLM 实例
    """
    if llm_provider in _OPENAI_PROVIDERS:
        provider_name, env_prefix = _OPENAI_PROVIDERS[llm_provider]
        api_key = os.getenv(f"{env_prefix}_API_KEY")
        base_url = os.getenv(f"{env_prefix}_BASEURL")
        model_name = os.getenv(f"{env_prefix}_MODEL_NAME")

        if not all([api_key, base_url, model_name]):
            missing = [k for k, v in [
                (f"{env_prefix}_API_KEY", api_key),
                (f"{env_prefix}_BASEURL", base_url),
                (f"{env_prefix}_MODEL_NAME", model_name),
            ] if not v]
            raise ValueError(f"{provider_name} API配置缺失: {', '.join(missing)}")

        print(f"✓ 已初始化{provider_name}客户端，使用模型: {model_name}")

        return ChatOpenAI(
            model=model_name,
            temperature=0,
            max_tokens=2000,
            timeout=30,
            api_key=api_key,
            base_url=base_url,
            max_retries=3,
        )

    raise ValueError(f"不支持的LLM提供商: {llm_provider}")