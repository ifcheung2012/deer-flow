# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import MessagesState

from src.prompts.planner_model import Plan
from src.rag import Resource


class State(MessagesState):
    """State for the agent system, extends MessagesState with next field."""
    # 代理系统的状态，扩展了MessagesState并添加了next字段

    # Runtime Variables
    # 运行时变量
    locale: str = "en-US"                     # 区域设置
    research_topic: str = ""                  # 研究主题
    observations: list[str] = []              # 观察结果列表
    resources: list[Resource] = []            # 资源列表
    plan_iterations: int = 0                  # 计划迭代次数
    current_plan: Plan | str = None           # 当前计划
    final_report: str = ""                    # 最终报告
    auto_accepted_plan: bool = False          # 自动接受计划
    enable_background_investigation: bool = True  # 启用背景调查
    background_investigation_results: str = None  # 背景调查结果
