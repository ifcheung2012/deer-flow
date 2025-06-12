# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Server script for running the DeerFlow API.
"""
# 用于运行DeerFlow API的服务器脚本

import argparse
import logging
import signal
import sys
import uvicorn

# Configure logging
# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def handle_shutdown(signum, frame):
    """Handle graceful shutdown on SIGTERM/SIGINT"""
    # 处理SIGTERM/SIGINT信号的优雅关闭
    logger.info("Received shutdown signal. Starting graceful shutdown...")
    sys.exit(0)


# Register signal handlers
# 注册信号处理器
signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

if __name__ == "__main__":
    # Parse command line arguments
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Run the DeerFlow API server")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (default: True except on Windows)",  # 启用自动重载（默认：除Windows外均为True）
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind the server to (default: localhost)",  # 服务器绑定的主机（默认：localhost）
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",  # 服务器绑定的端口（默认：8000）
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level (default: info)",  # 日志级别（默认：info）
    )

    args = parser.parse_args()

    # Determine reload setting
    # 确定重载设置
    reload = False
    if args.reload:
        reload = True

    try:
        logger.info(f"Starting DeerFlow API server on {args.host}:{args.port}")
        uvicorn.run(
            "src.server:app",
            host=args.host,
            port=args.port,
            reload=reload,
            log_level=args.log_level,
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)
