# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import enum
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量


class SearchEngine(enum.Enum):
    """搜索引擎枚举类"""
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    BRAVE_SEARCH = "brave_search"
    ARXIV = "arxiv"


# Tool configuration
# 工具配置
SELECTED_SEARCH_ENGINE = os.getenv("SEARCH_API", SearchEngine.TAVILY.value)  # 选择的搜索引擎


class RAGProvider(enum.Enum):
    """RAG提供者枚举类"""
    RAGFLOW = "ragflow"


SELECTED_RAG_PROVIDER = os.getenv("RAG_PROVIDER")  # 选择的RAG提供者
