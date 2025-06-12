# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from pydantic import BaseModel, Field

from src.rag.retriever import Resource


class RAGConfigResponse(BaseModel):
    """Response model for RAG config."""
    # RAG配置响应模型

    provider: str | None = Field(
        None, description="The provider of the RAG, default is ragflow"
        # RAG的提供者，默认为ragflow
    )


class RAGResourceRequest(BaseModel):
    """Request model for RAG resource."""
    # RAG资源请求模型

    query: str | None = Field(
        None, description="The query of the resource need to be searched"
        # 需要搜索的资源的查询
    )


class RAGResourcesResponse(BaseModel):
    """Response model for RAG resources."""
    # RAG资源响应模型

    resources: list[Resource] = Field(..., description="The resources of the RAG")
    # RAG的资源列表
