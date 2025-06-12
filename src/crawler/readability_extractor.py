# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from readabilipy import simple_json_from_html_string  # 导入从HTML字符串创建简单JSON的函数

from .article import Article


class ReadabilityExtractor:
    """可读性提取器类，用于从HTML内容中提取可读的文章内容"""
    
    def extract_article(self, html: str) -> Article:
        """
        从HTML内容中提取文章
        
        参数:
            html: HTML内容字符串
            
        返回:
            提取的文章对象
        """
        article = simple_json_from_html_string(html, use_readability=True)  # 使用readability算法从HTML提取JSON
        return Article(
            title=article.get("title"),      # 获取文章标题
            html_content=article.get("content"),  # 获取文章内容
        )
