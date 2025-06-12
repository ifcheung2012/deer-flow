# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os

import requests

logger = logging.getLogger(__name__)  # 获取日志记录器


class JinaClient:
    """Jina客户端类，用于与Jina API交互爬取网页内容"""
    
    def crawl(self, url: str, return_format: str = "html") -> str:
        """
        使用Jina API爬取指定URL的网页内容
        
        参数:
            url: 要爬取的网页URL
            return_format: 返回格式，默认为"html"
            
        返回:
            爬取的网页内容
        """
        headers = {
            "Content-Type": "application/json",  # 内容类型
            "X-Return-Format": return_format,    # 返回格式
        }
        if os.getenv("JINA_API_KEY"):
            headers["Authorization"] = f"Bearer {os.getenv('JINA_API_KEY')}"  # 添加API密钥认证
        else:
            logger.warning(
                "Jina API key is not set. Provide your own key to access a higher rate limit. See https://jina.ai/reader for more information."
                # Jina API密钥未设置。提供您自己的密钥以访问更高的速率限制。更多信息请参见https://jina.ai/reader
            )
        data = {"url": url}  # 请求数据
        response = requests.post("https://r.jina.ai/", headers=headers, json=data)  # 发送POST请求
        return response.text  # 返回响应文本
