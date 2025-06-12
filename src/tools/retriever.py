# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import List, Optional, Type
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

from src.config.tools import SELECTED_RAG_PROVIDER
from src.rag import Document, Retriever, Resource, build_retriever

logger = logging.getLogger(__name__)  # 获取日志记录器


class RetrieverInput(BaseModel):
    """检索工具的输入模型"""
    keywords: str = Field(description="search keywords to look up")  # 要查找的搜索关键词


class RetrieverTool(BaseTool):
    """本地检索工具类"""
    name: str = "local_search_tool"  # 工具名称
    description: str = (
        "Useful for retrieving information from the file with `rag://` uri prefix, it should be higher priority than the web search or writing code. Input should be a search keywords."
        # 用于从带有`rag://`uri前缀的文件中检索信息，它应该比网络搜索或编写代码具有更高的优先级。输入应该是搜索关键词。
    )
    args_schema: Type[BaseModel] = RetrieverInput  # 参数模式

    retriever: Retriever = Field(default_factory=Retriever)  # 检索器
    resources: list[Resource] = Field(default_factory=list)  # 资源列表

    def _run(
        self,
        keywords: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> list[Document]:
        """执行检索操作"""
        logger.info(
            f"Retriever tool query: {keywords}", extra={"resources": self.resources}
        )  # 记录检索工具查询信息
        documents = self.retriever.query_relevant_documents(keywords, self.resources)  # 查询相关文档
        if not documents:
            return "No results found from the local knowledge base."  # 从本地知识库中未找到结果
        return [doc.to_dict() for doc in documents]  # 返回文档字典列表

    async def _arun(
        self,
        keywords: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> list[Document]:
        """异步执行检索操作"""
        return self._run(keywords, run_manager.get_sync())  # 调用同步方法


def get_retriever_tool(resources: List[Resource]) -> RetrieverTool | None:
    """
    获取检索工具
    
    参数:
        resources: 资源列表
        
    返回:
        检索工具实例或None
    """
    if not resources:
        return None  # 如果没有资源，则返回None
    logger.info(f"create retriever tool: {SELECTED_RAG_PROVIDER}")  # 记录创建检索工具信息
    retriever = build_retriever()  # 构建检索器

    if not retriever:
        return None  # 如果没有检索器，则返回None
    return RetrieverTool(retriever=retriever, resources=resources)  # 返回检索工具实例


if __name__ == "__main__":
    # 测试代码
    resources = [
        Resource(
            uri="rag://dataset/1c7e2ea4362911f09a41c290d4b6a7f0",
            title="西游记",
            description="西游记是中国古代四大名著之一，讲述了唐僧师徒四人西天取经的故事。",
        )
    ]
    retriever_tool = get_retriever_tool(resources)  # 获取检索工具
    print(retriever_tool.name)  # 打印名称
    print(retriever_tool.description)  # 打印描述
    print(retriever_tool.args)  # 打印参数
    print(retriever_tool.invoke("三打白骨精"))  # 调用工具查询"三打白骨精"
