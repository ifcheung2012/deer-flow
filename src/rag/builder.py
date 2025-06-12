# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from src.config.tools import SELECTED_RAG_PROVIDER, RAGProvider
from src.rag.ragflow import RAGFlowProvider
from src.rag.retriever import Retriever


def build_retriever() -> Retriever | None:
    """
    构建检索器实例
    
    根据配置的RAG提供者类型创建相应的检索器实例
    
    返回:
        检索器实例或None（如果未配置RAG提供者）
    """
    if SELECTED_RAG_PROVIDER == RAGProvider.RAGFLOW.value:
        return RAGFlowProvider()  # 返回RAGFlow提供者实例
    elif SELECTED_RAG_PROVIDER:
        raise ValueError(f"Unsupported RAG provider: {SELECTED_RAG_PROVIDER}")  # 不支持的RAG提供者
    return None  # 如果未配置RAG提供者，则返回None
