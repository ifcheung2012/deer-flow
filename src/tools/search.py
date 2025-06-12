# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os

from langchain_community.tools import BraveSearch, DuckDuckGoSearchResults
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper, BraveSearchWrapper

from src.config import SearchEngine, SELECTED_SEARCH_ENGINE
from src.tools.tavily_search.tavily_search_results_with_images import (
    TavilySearchResultsWithImages,
)

from src.tools.decorators import create_logged_tool

logger = logging.getLogger(__name__)  # 获取日志记录器

# Create logged versions of the search tools
# 创建搜索工具的日志版本
LoggedTavilySearch = create_logged_tool(TavilySearchResultsWithImages)  # Tavily搜索（带图像）
LoggedDuckDuckGoSearch = create_logged_tool(DuckDuckGoSearchResults)  # DuckDuckGo搜索结果
LoggedBraveSearch = create_logged_tool(BraveSearch)  # Brave搜索
LoggedArxivSearch = create_logged_tool(ArxivQueryRun)  # Arxiv查询运行


# Get the selected search tool
# 获取选定的搜索工具
def get_web_search_tool(max_search_results: int):
    """
    根据配置的搜索引擎返回相应的网页搜索工具
    
    参数:
        max_search_results: 最大搜索结果数量
        
    返回:
        配置的搜索工具实例
    """
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        return LoggedTavilySearch(
            name="web_search",
            max_results=max_search_results,
            include_raw_content=True,  # 包含原始内容
            include_images=True,  # 包含图像
            include_image_descriptions=True,  # 包含图像描述
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.DUCKDUCKGO.value:
        return LoggedDuckDuckGoSearch(name="web_search", max_results=max_search_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BRAVE_SEARCH.value:
        return LoggedBraveSearch(
            name="web_search",
            search_wrapper=BraveSearchWrapper(
                api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),  # 从环境变量获取API密钥
                search_kwargs={"count": max_search_results},  # 搜索参数
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ARXIV.value:
        return LoggedArxivSearch(
            name="web_search",
            api_wrapper=ArxivAPIWrapper(
                top_k_results=max_search_results,  # 前k个结果
                load_max_docs=max_search_results,  # 加载的最大文档数
                load_all_available_meta=True,  # 加载所有可用的元数据
            ),
        )
    else:
        raise ValueError(f"Unsupported search engine: {SELECTED_SEARCH_ENGINE}")  # 不支持的搜索引擎


if __name__ == "__main__":
    # 测试代码
    results = LoggedDuckDuckGoSearch(
        name="web_search", max_results=3, output_format="list"
    )
    print(results.name)  # 打印名称
    print(results.description)  # 打印描述
    print(results.args)  # 打印参数
    # .invoke("cute panda")
    # print(json.dumps(results, indent=2, ensure_ascii=False))
