# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import re
from urllib.parse import urljoin

from markdownify import markdownify as md


class Article:
    """文章类，用于表示从网页爬取的文章内容"""
    url: str  # 文章URL

    def __init__(self, title: str, html_content: str):
        """
        初始化文章对象
        
        参数:
            title: 文章标题
            html_content: 文章的HTML内容
        """
        self.title = title
        self.html_content = html_content

    def to_markdown(self, including_title: bool = True) -> str:
        """
        将文章转换为Markdown格式
        
        参数:
            including_title: 是否包含标题
            
        返回:
            Markdown格式的文章内容
        """
        markdown = ""
        if including_title:
            markdown += f"# {self.title}\n\n"  # 添加标题
        markdown += md(self.html_content)  # 将HTML转换为Markdown
        return markdown

    def to_message(self) -> list[dict]:
        """
        将文章转换为消息格式，分离文本和图片
        
        返回:
            包含文本和图片URL的消息列表
        """
        image_pattern = r"!\[.*?\]\((.*?)\)"  # Markdown图片正则表达式

        content: list[dict[str, str]] = []
        parts = re.split(image_pattern, self.to_markdown())  # 按图片分割内容

        for i, part in enumerate(parts):
            if i % 2 == 1:
                # 图片URL部分
                image_url = urljoin(self.url, part.strip())  # 构建完整图片URL
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            else:
                # 文本部分
                content.append({"type": "text", "text": part.strip()})

        return content
