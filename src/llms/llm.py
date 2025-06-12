# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any, Dict
import os

from langchain_openai import ChatOpenAI

from src.config import load_yaml_config
from src.config.agents import LLMType

# Cache for LLM instances
# LLM实例的缓存
_llm_cache: dict[LLMType, ChatOpenAI] = {}


def _get_env_llm_conf(llm_type: str) -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables.
    Environment variables should follow the format: {LLM_TYPE}__{KEY}
    e.g., BASIC_MODEL__api_key, BASIC_MODEL__base_url
    """
    # 从环境变量获取LLM配置
    # 环境变量应遵循格式：{LLM_TYPE}__{KEY}
    # 例如：BASIC_MODEL__api_key, BASIC_MODEL__base_url
    prefix = f"{llm_type.upper()}_MODEL__"
    conf = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            conf_key = key[len(prefix) :].lower()
            conf[conf_key] = value
    return conf


def _create_llm_use_conf(llm_type: LLMType, conf: Dict[str, Any]) -> ChatOpenAI:
    """
    创建LLM实例使用配置
    
    参数:
        llm_type: LLM类型
        conf: 配置字典
    
    返回:
        ChatOpenAI实例
    """
    llm_type_map = {
        "reasoning": conf.get("REASONING_MODEL", {}),  # 推理模型
        "basic": conf.get("BASIC_MODEL", {}),          # 基础模型
        "vision": conf.get("VISION_MODEL", {}),        # 视觉模型
    }
    llm_conf = llm_type_map.get(llm_type)
    if not isinstance(llm_conf, dict):
        raise ValueError(f"Invalid LLM Conf: {llm_type}")  # 无效的LLM配置
    # Get configuration from environment variables
    # 从环境变量获取配置
    env_conf = _get_env_llm_conf(llm_type)

    # Merge configurations, with environment variables taking precedence
    # 合并配置，环境变量优先
    merged_conf = {**llm_conf, **env_conf}

    if not merged_conf:
        raise ValueError(f"Unknown LLM Conf: {llm_type}")  # 未知的LLM配置

    return ChatOpenAI(**merged_conf)


def get_llm_by_type(
    llm_type: LLMType,
) -> ChatOpenAI:
    """
    Get LLM instance by type. Returns cached instance if available.
    """
    # 通过类型获取LLM实例。如果可用，返回缓存的实例。
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]

    conf = load_yaml_config(
        str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())
    )
    llm = _create_llm_use_conf(llm_type, conf)
    _llm_cache[llm_type] = llm
    return llm


# In the future, we will use reasoning_llm and vl_llm for different purposes
# 将来，我们将使用reasoning_llm和vl_llm用于不同目的
# reasoning_llm = get_llm_by_type("reasoning")
# vl_llm = get_llm_by_type("vision")
