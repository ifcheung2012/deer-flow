# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)  # 获取日志记录器


async def _get_tools_from_client_session(
    client_context_manager: Any, timeout_seconds: int = 10
) -> List:
    """
    Helper function to get tools from a client session.

    Args:
        client_context_manager: A context manager that returns (read, write) functions
        timeout_seconds: Timeout in seconds for the read operation

    Returns:
        List of available tools from the MCP server

    Raises:
        Exception: If there's an error during the process
    """
    # 从客户端会话获取工具的辅助函数
    #
    # 参数:
    #     client_context_manager: 返回(read, write)函数的上下文管理器
    #     timeout_seconds: 读取操作的超时时间（秒）
    #
    # 返回:
    #     MCP服务器提供的可用工具列表
    #
    # 抛出:
    #     Exception: 如果在过程中出现错误
    
    async with client_context_manager as (read, write):
        async with ClientSession(
            read, write, read_timeout_seconds=timedelta(seconds=timeout_seconds)
        ) as session:
            # Initialize the connection
            # 初始化连接
            await session.initialize()
            # List available tools
            # 列出可用工具
            listed_tools = await session.list_tools()
            return listed_tools.tools


async def load_mcp_tools(
    server_type: str,
    command: Optional[str] = None,
    args: Optional[List[str]] = None,
    url: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout_seconds: int = 60,  # Longer default timeout for first-time executions
) -> List:
    """
    Load tools from an MCP server.

    Args:
        server_type: The type of MCP server connection (stdio or sse)
        command: The command to execute (for stdio type)
        args: Command arguments (for stdio type)
        url: The URL of the SSE server (for sse type)
        env: Environment variables
        timeout_seconds: Timeout in seconds (default: 60 for first-time executions)

    Returns:
        List of available tools from the MCP server

    Raises:
        HTTPException: If there's an error loading the tools
    """
    # 从MCP服务器加载工具
    #
    # 参数:
    #     server_type: MCP服务器连接类型（stdio或sse）
    #     command: 要执行的命令（用于stdio类型）
    #     args: 命令参数（用于stdio类型）
    #     url: SSE服务器的URL（用于sse类型）
    #     env: 环境变量
    #     timeout_seconds: 超时时间（秒）（默认：60秒，用于首次执行）
    #
    # 返回:
    #     MCP服务器提供的可用工具列表
    #
    # 抛出:
    #     HTTPException: 如果加载工具时出错
    
    try:
        if server_type == "stdio":
            if not command:
                raise HTTPException(
                    status_code=400, detail="Command is required for stdio type"
                    # 错误：stdio类型需要提供命令
                )

            server_params = StdioServerParameters(
                command=command,  # Executable 可执行文件
                args=args,  # Optional command line arguments 可选的命令行参数
                env=env,  # Optional environment variables 可选的环境变量
            )

            return await _get_tools_from_client_session(
                stdio_client(server_params), timeout_seconds
            )

        elif server_type == "sse":
            if not url:
                raise HTTPException(
                    status_code=400, detail="URL is required for sse type"
                    # 错误：sse类型需要提供URL
                )

            return await _get_tools_from_client_session(
                sse_client(url=url), timeout_seconds
            )

        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported server type: {server_type}"
                # 错误：不支持的服务器类型
            )

    except Exception as e:
        if not isinstance(e, HTTPException):
            logger.exception(f"Error loading MCP tools: {str(e)}")  # 加载MCP工具时出错
            raise HTTPException(status_code=500, detail=str(e))
        raise
