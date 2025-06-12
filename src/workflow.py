# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import asyncio
import logging
from src.graph import build_graph

# Configure logging
# 配置日志记录
logging.basicConfig(
    level=logging.INFO,  # Default level is INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """
    启用调试级别的日志记录，以获取更详细的执行信息
    
    该函数将src模块的日志级别设置为DEBUG
    """
    # 启用调试级别的日志记录，以获取更详细的执行信息
    logging.getLogger("src").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

# Create the graph
# 创建图
graph = build_graph()  # 构建工作流图


async def run_agent_workflow_async(
    user_input: str,
    debug: bool = False,
    max_plan_iterations: int = 1,
    max_step_num: int = 3,
    enable_background_investigation: bool = True,
):
    """
    使用给定的用户输入异步运行代理工作流
    
    参数:
        user_input: 用户的查询或请求
        debug: 如果为True，启用调试级别的日志记录
        max_plan_iterations: 计划迭代的最大次数
        max_step_num: 计划中步骤的最大数量
        enable_background_investigation: 如果为True，在规划前执行网络搜索以增强上下文
    
    返回:
        工作流完成后的最终状态
    """
    # 使用给定的用户输入异步运行代理工作流
    #
    # 参数：
    #     user_input: 用户的查询或请求
    #     debug: 如果为True，启用调试级别的日志记录
    #     max_plan_iterations: 计划迭代的最大次数
    #     max_step_num: 计划中步骤的最大数量
    #     enable_background_investigation: 如果为True，在规划前执行网络搜索以增强上下文
    #
    # 返回：
    #     工作流完成后的最终状态
    if not user_input:
        raise ValueError("Input could not be empty")  # 输入不能为空

    if debug:
        enable_debug_logging()  # 如果debug为True，启用调试日志

    logger.info(f"Starting async workflow with user input: {user_input}")  # 记录开始异步工作流的信息
    initial_state = {
        # Runtime Variables
        # 运行时变量
        "messages": [{"role": "user", "content": user_input}],  # 初始消息
        "auto_accepted_plan": True,  # 自动接受计划
        "enable_background_investigation": enable_background_investigation,  # 启用背景调查
    }
    config = {
        "configurable": {
            "thread_id": "default",  # 默认线程ID
            "max_plan_iterations": max_plan_iterations,  # 最大计划迭代次数
            "max_step_num": max_step_num,  # 最大步骤数
            "mcp_settings": {
                "servers": {
                    "mcp-github-trending": {
                        "transport": "stdio",  # 传输方式
                        "command": "uvx",  # 命令
                        "args": ["mcp-github-trending"],  # 参数
                        "enabled_tools": ["get_github_trending_repositories"],  # 启用的工具
                        "add_to_agents": ["researcher"],  # 添加到代理
                    }
                }
            },
        },
        "recursion_limit": 100,  # 递归限制
    }
    last_message_cnt = 0  # 上一次消息计数
    async for s in graph.astream(
        input=initial_state, config=config, stream_mode="values"
    ):  # 异步流式处理
        try:
            if isinstance(s, dict) and "messages" in s:
                if len(s["messages"]) <= last_message_cnt:
                    continue  # 如果消息数量没有增加，则继续
                last_message_cnt = len(s["messages"])  # 更新消息计数
                message = s["messages"][-1]  # 获取最新消息
                if isinstance(message, tuple):
                    print(message)  # 如果消息是元组，直接打印
                else:
                    message.pretty_print()  # 否则使用pretty_print方法打印
            else:
                # For any other output format
                # 对于任何其他输出格式
                print(f"Output: {s}")  # 打印输出
        except Exception as e:
            logger.error(f"Error processing stream output: {e}")  # 记录处理流输出错误
            print(f"Error processing output: {str(e)}")  # 打印错误信息

    logger.info("Async workflow completed successfully")  # 异步工作流成功完成


if __name__ == "__main__":
    print(graph.get_graph(xray=True).draw_mermaid())  # 打印图的Mermaid绘图
