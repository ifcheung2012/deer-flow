# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Entry point script for the DeerFlow project.
"""
# DeerFlow项目的入口脚本

import argparse
import asyncio

from InquirerPy import inquirer

from src.config.questions import BUILT_IN_QUESTIONS, BUILT_IN_QUESTIONS_ZH_CN
from src.workflow import run_agent_workflow_async


def ask(
    question,
    debug=False,
    max_plan_iterations=1,
    max_step_num=3,
    enable_background_investigation=True,
):
    """Run the agent workflow with the given question.

    Args:
        question: The user's query or request
        debug: If True, enables debug level logging
        max_plan_iterations: Maximum number of plan iterations
        max_step_num: Maximum number of steps in a plan
        enable_background_investigation: If True, performs web search before planning to enhance context
    """
    # 使用给定的问题运行代理工作流
    #
    # 参数：
    #     question: 用户的查询或请求
    #     debug: 如果为True，启用调试级别的日志记录
    #     max_plan_iterations: 计划迭代的最大次数
    #     max_step_num: 计划中步骤的最大数量
    #     enable_background_investigation: 如果为True，在规划前执行网络搜索以增强上下文
    asyncio.run(
        run_agent_workflow_async(
            user_input=question,
            debug=debug,
            max_plan_iterations=max_plan_iterations,
            max_step_num=max_step_num,
            enable_background_investigation=enable_background_investigation,
        )
    )


def main(
    debug=False,
    max_plan_iterations=1,
    max_step_num=3,
    enable_background_investigation=True,
):
    """Interactive mode with built-in questions.

    Args:
        enable_background_investigation: If True, performs web search before planning to enhance context
        debug: If True, enables debug level logging
        max_plan_iterations: Maximum number of plan iterations
        max_step_num: Maximum number of steps in a plan
    """
    # 带有内置问题的交互模式
    #
    # 参数：
    #     enable_background_investigation: 如果为True，在规划前执行网络搜索以增强上下文
    #     debug: 如果为True，启用调试级别的日志记录
    #     max_plan_iterations: 计划迭代的最大次数
    #     max_step_num: 计划中步骤的最大数量
    
    # First select language
    # 首先选择语言
    language = inquirer.select(
        message="Select language / 选择语言:",
        choices=["English", "中文"],
    ).execute()

    # Choose questions based on language
    # 根据语言选择问题
    questions = (
        BUILT_IN_QUESTIONS if language == "English" else BUILT_IN_QUESTIONS_ZH_CN
    )
    ask_own_option = (
        "[Ask my own question]" if language == "English" else "[自定义问题]"
    )

    # Select a question
    # 选择一个问题
    initial_question = inquirer.select(
        message=(
            "What do you want to know?" if language == "English" else "您想了解什么?"
        ),
        choices=[ask_own_option] + questions,
    ).execute()

    if initial_question == ask_own_option:
        initial_question = inquirer.text(
            message=(
                "What do you want to know?"
                if language == "English"
                else "您想了解什么?"
            ),
        ).execute()

    # Pass all parameters to ask function
    # 将所有参数传递给ask函数
    ask(
        question=initial_question,
        debug=debug,
        max_plan_iterations=max_plan_iterations,
        max_step_num=max_step_num,
        enable_background_investigation=enable_background_investigation,
    )


if __name__ == "__main__":
    # Set up argument parser
    # 设置参数解析器
    parser = argparse.ArgumentParser(description="Run the Deer")
    parser.add_argument("query", nargs="*", help="The query to process")  # 要处理的查询
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode with built-in questions",  # 以交互模式运行，使用内置问题
    )
    parser.add_argument(
        "--max_plan_iterations",
        type=int,
        default=1,
        help="Maximum number of plan iterations (default: 1)",  # 计划迭代的最大次数（默认：1）
    )
    parser.add_argument(
        "--max_step_num",
        type=int,
        default=3,
        help="Maximum number of steps in a plan (default: 3)",  # 计划中步骤的最大数量（默认：3）
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")  # 启用调试日志记录
    parser.add_argument(
        "--no-background-investigation",
        action="store_false",
        dest="enable_background_investigation",
        help="Disable background investigation before planning",  # 在规划前禁用背景调查
    )

    args = parser.parse_args()

    if args.interactive:
        # Pass command line arguments to main function
        # 将命令行参数传递给main函数
        main(
            debug=args.debug,
            max_plan_iterations=args.max_plan_iterations,
            max_step_num=args.max_step_num,
            enable_background_investigation=args.enable_background_investigation,
        )
    else:
        # Parse user input from command line arguments or user input
        # 从命令行参数或用户输入解析用户输入
        if args.query:
            user_query = " ".join(args.query)
        else:
            user_query = input("Enter your query: ")  # 输入您的查询

        # Run the agent workflow with the provided parameters
        # 使用提供的参数运行代理工作流
        ask(
            question=user_query,
            debug=args.debug,
            max_plan_iterations=args.max_plan_iterations,
            max_step_num=args.max_step_num,
            enable_background_investigation=args.enable_background_investigation,
        )
