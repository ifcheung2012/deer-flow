# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import abc
from pydantic import BaseModel, Field


class Chunk:
    """文档块类，表示文档的一个片段"""
    content: str  # 内容
    similarity: float  # 相似度

    def __init__(self, content: str, similarity: float):
        """
        初始化文档块
        
        参数:
            content: 块内容
            similarity: 与查询的相似度
        """
        self.content = content
        self.similarity = similarity


class Document:
    """
    Document is a class that represents a document.
    """
    # 文档类，表示一个文档

    id: str  # 文档ID
    url: str | None = None  # 文档URL
    title: str | None = None  # 文档标题
    chunks: list[Chunk] = []  # 文档块列表

    def __init__(
        self,
        id: str,
        url: str | None = None,
        title: str | None = None,
        chunks: list[Chunk] = [],
    ):
        """
        初始化文档
        
        参数:
            id: 文档ID
            url: 文档URL
            title: 文档标题
            chunks: 文档块列表
        """
        self.id = id
        self.url = url
        self.title = title
        self.chunks = chunks

    def to_dict(self) -> dict:
        """
        将文档转换为字典
        
        返回:
            文档的字典表示
        """
        d = {
            "id": self.id,
            "content": "\n\n".join([chunk.content for chunk in self.chunks]),  # 合并所有块的内容
        }
        if self.url:
            d["url"] = self.url
        if self.title:
            d["title"] = self.title
        return d


class Resource(BaseModel):
    """
    Resource is a class that represents a resource.
    """
    # 资源类，表示一个资源

    uri: str = Field(..., description="The URI of the resource")  # 资源的URI
    title: str = Field(..., description="The title of the resource")  # 资源的标题
    description: str | None = Field("", description="The description of the resource")  # 资源的描述


class Retriever(abc.ABC):
    """
    Define a RAG provider, which can be used to query documents and resources.
    """
    # 定义RAG提供者，可用于查询文档和资源

    @abc.abstractmethod
    def list_resources(self, query: str | None = None) -> list[Resource]:
        """
        List resources from the rag provider.
        """
        # 列出RAG提供者中的资源
        pass

    @abc.abstractmethod
    def query_relevant_documents(
        self, query: str, resources: list[Resource] = []
    ) -> list[Document]:
        """
        Query relevant documents from the resources.
        """
        # 从资源中查询相关文档
        pass
