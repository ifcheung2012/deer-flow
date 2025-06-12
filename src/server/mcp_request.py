# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MCPServerMetadataRequest(BaseModel):
    """Request model for MCP server metadata."""
    # MCP服务器元数据请求模型

    transport: str = Field(
        ..., description="The type of MCP server connection (stdio or sse)"
        # MCP服务器连接类型（stdio或sse）
    )
    command: Optional[str] = Field(
        None, description="The command to execute (for stdio type)"
        # 要执行的命令（用于stdio类型）
    )
    args: Optional[List[str]] = Field(
        None, description="Command arguments (for stdio type)"
        # 命令参数（用于stdio类型）
    )
    url: Optional[str] = Field(
        None, description="The URL of the SSE server (for sse type)"
        # SSE服务器的URL（用于sse类型）
    )
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    # 环境变量
    timeout_seconds: Optional[int] = Field(
        None, description="Optional custom timeout in seconds for the operation"
        # 操作的可选自定义超时时间（秒）
    )


class MCPServerMetadataResponse(BaseModel):
    """Response model for MCP server metadata."""
    # MCP服务器元数据响应模型

    transport: str = Field(
        ..., description="The type of MCP server connection (stdio or sse)"
        # MCP服务器连接类型（stdio或sse）
    )
    command: Optional[str] = Field(
        None, description="The command to execute (for stdio type)"
        # 要执行的命令（用于stdio类型）
    )
    args: Optional[List[str]] = Field(
        None, description="Command arguments (for stdio type)"
        # 命令参数（用于stdio类型）
    )
    url: Optional[str] = Field(
        None, description="The URL of the SSE server (for sse type)"
        # SSE服务器的URL（用于sse类型）
    )
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    # 环境变量
    tools: List = Field(
        default_factory=list, description="Available tools from the MCP server"
        # MCP服务器提供的可用工具
    )
