# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import Annotated

from langchain_core.tools import tool
from .decorators import log_io

from src.crawler import Crawler

logger = logging.getLogger(__name__)  # 获取日志记录器


@tool
@log_io
def crawl_tool(
    url: Annotated[str, "The url to crawl."],  # 要爬取的URL
) -> str:
    """Use this to crawl a url and get a readable content in markdown format."""
    # 使用此工具爬取URL并获取可读的markdown格式内容
    try:
        crawler = Crawler()  # 创建爬虫实例
        article = crawler.crawl(url)  # 爬取URL
        return {"url": url, "crawled_content": article.to_markdown()[:1000]}  # 返回URL和爬取内容（限制为1000字符）
    except BaseException as e:
        error_msg = f"Failed to crawl. Error: {repr(e)}"  # 爬取失败。错误：{错误信息}
        logger.error(error_msg)  # 记录错误
        return error_msg  # 返回错误信息
