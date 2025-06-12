# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import sys

from .article import Article
from .jina_client import JinaClient
from .readability_extractor import ReadabilityExtractor


class Crawler:
    """爬虫类，用于爬取网页并提取文章内容"""
    
    def crawl(self, url: str) -> Article:
        """
        爬取指定URL的网页并提取文章内容
        
        参数:
            url: 要爬取的网页URL
            
        返回:
            提取的文章对象
        """
        # To help LLMs better understand content, we extract clean
        # articles from HTML, convert them to markdown, and split
        # them into text and image blocks for one single and unified
        # LLM message.
        # 为了帮助LLM更好地理解内容，我们从HTML中提取干净的文章，
        # 将它们转换为markdown，并将它们分割成文本和图像块，
        # 以便形成单一统一的LLM消息。
        #
        # Jina is not the best crawler on readability, however it's
        # much easier and free to use.
        # Jina在可读性方面不是最好的爬虫，但它更容易使用且免费。
        #
        # Instead of using Jina's own markdown converter, we'll use
        # our own solution to get better readability results.
        # 我们不使用Jina自己的markdown转换器，而是使用我们自己的解决方案
        # 来获得更好的可读性结果。
        
        jina_client = JinaClient()  # 创建Jina客户端
        html = jina_client.crawl(url, return_format="html")  # 使用Jina爬取HTML
        extractor = ReadabilityExtractor()  # 创建可读性提取器
        article = extractor.extract_article(html)  # 从HTML中提取文章
        article.url = url  # 设置文章URL
        return article  # 返回文章对象
