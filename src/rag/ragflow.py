# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import requests
from src.rag.retriever import Chunk, Document, Resource, Retriever
from urllib.parse import urlparse


class RAGFlowProvider(Retriever):
    """
    RAGFlowProvider is a provider that uses RAGFlow to retrieve documents.
    """
    # RAGFlowProvider是使用RAGFlow检索文档的提供者

    api_url: str  # API URL
    api_key: str  # API密钥
    page_size: int = 10  # 页面大小

    def __init__(self):
        """
        初始化RAGFlow提供者
        
        从环境变量中获取必要的配置信息
        """
        api_url = os.getenv("RAGFLOW_API_URL")
        if not api_url:
            raise ValueError("RAGFLOW_API_URL is not set")  # RAGFLOW_API_URL未设置
        self.api_url = api_url

        api_key = os.getenv("RAGFLOW_API_KEY")
        if not api_key:
            raise ValueError("RAGFLOW_API_KEY is not set")  # RAGFLOW_API_KEY未设置
        self.api_key = api_key

        page_size = os.getenv("RAGFLOW_PAGE_SIZE")
        if page_size:
            self.page_size = int(page_size)

    def query_relevant_documents(
        self, query: str, resources: list[Resource] = []
    ) -> list[Document]:
        """
        查询与给定查询相关的文档
        
        参数:
            query: 查询字符串
            resources: 资源列表
            
        返回:
            相关文档列表
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        dataset_ids: list[str] = []  # 数据集ID列表
        document_ids: list[str] = []  # 文档ID列表

        for resource in resources:
            dataset_id, document_id = parse_uri(resource.uri)  # 解析URI
            dataset_ids.append(dataset_id)
            if document_id:
                document_ids.append(document_id)

        payload = {
            "question": query,  # 问题/查询
            "dataset_ids": dataset_ids,  # 数据集ID
            "document_ids": document_ids,  # 文档ID
            "page_size": self.page_size,  # 页面大小
        }

        response = requests.post(
            f"{self.api_url}/api/v1/retrieval", headers=headers, json=payload
        )  # 发送POST请求

        if response.status_code != 200:
            raise Exception(f"Failed to query documents: {response.text}")  # 查询文档失败

        result = response.json()
        data = result.get("data", {})
        doc_aggs = data.get("doc_aggs", [])
        docs: dict[str, Document] = {
            doc.get("doc_id"): Document(
                id=doc.get("doc_id"),
                title=doc.get("doc_name"),
                chunks=[],
            )
            for doc in doc_aggs
        }  # 创建文档字典

        for chunk in data.get("chunks", []):
            doc = docs.get(chunk.get("document_id"))
            if doc:
                doc.chunks.append(
                    Chunk(
                        content=chunk.get("content"),  # 块内容
                        similarity=chunk.get("similarity"),  # 相似度
                    )
                )  # 添加块到文档

        return list(docs.values())  # 返回文档列表

    def list_resources(self, query: str | None = None) -> list[Resource]:
        """
        列出可用的资源
        
        参数:
            query: 可选的查询字符串，用于过滤资源
            
        返回:
            资源列表
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        params = {}
        if query:
            params["name"] = query  # 如果有查询，添加到参数中

        response = requests.get(
            f"{self.api_url}/api/v1/datasets", headers=headers, params=params
        )  # 发送GET请求

        if response.status_code != 200:
            raise Exception(f"Failed to list resources: {response.text}")  # 列出资源失败

        result = response.json()
        resources = []

        for item in result.get("data", []):
            item = Resource(
                uri=f"rag://dataset/{item.get('id')}",  # 资源URI
                title=item.get("name", ""),  # 资源标题
                description=item.get("description", ""),  # 资源描述
            )
            resources.append(item)

        return resources  # 返回资源列表


def parse_uri(uri: str) -> tuple[str, str]:
    """
    解析RAG URI
    
    参数:
        uri: RAG URI字符串
        
    返回:
        (数据集ID, 文档ID)元组
    """
    parsed = urlparse(uri)
    if parsed.scheme != "rag":
        raise ValueError(f"Invalid URI: {uri}")  # 无效的URI
    return parsed.path.split("/")[1], parsed.fragment  # 返回数据集ID和文档ID
