# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.prompts.planner_model import StepType

from .types import State
from .nodes import (
    coordinator_node,
    planner_node,
    reporter_node,
    research_team_node,
    researcher_node,
    coder_node,
    human_feedback_node,
    background_investigation_node,
)


def continue_to_running_research_team(state: State):
    """决定研究团队下一步执行的节点"""
    current_plan = state.get("current_plan")
    if not current_plan or not current_plan.steps:
        return "planner"  # 如果没有当前计划或计划步骤，返回规划员
    if all(step.execution_res for step in current_plan.steps):
        return "planner"  # 如果所有步骤都已执行，返回规划员
    for step in current_plan.steps:
        if not step.execution_res:
            break  # 找到第一个未执行的步骤
    if step.step_type and step.step_type == StepType.RESEARCH:
        return "researcher"  # 如果是研究类型的步骤，返回研究员
    if step.step_type and step.step_type == StepType.PROCESSING:
        return "coder"  # 如果是处理类型的步骤，返回编码员
    return "planner"  # 默认返回规划员


def _build_base_graph():
    """Build and return the base state graph with all nodes and edges."""
    # 构建并返回包含所有节点和边的基础状态图
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")  # 添加从开始到协调员的边
    builder.add_node("coordinator", coordinator_node)  # 添加协调员节点
    builder.add_node("background_investigator", background_investigation_node)  # 添加背景调查员节点
    builder.add_node("planner", planner_node)  # 添加规划员节点
    builder.add_node("reporter", reporter_node)  # 添加报告员节点
    builder.add_node("research_team", research_team_node)  # 添加研究团队节点
    builder.add_node("researcher", researcher_node)  # 添加研究员节点
    builder.add_node("coder", coder_node)  # 添加编码员节点
    builder.add_node("human_feedback", human_feedback_node)  # 添加人类反馈节点
    builder.add_edge("background_investigator", "planner")  # 添加从背景调查员到规划员的边
    builder.add_conditional_edges(
        "research_team",
        continue_to_running_research_team,
        ["planner", "researcher", "coder"],
    )  # 添加从研究团队到规划员、研究员或编码员的条件边
    builder.add_edge("reporter", END)  # 添加从报告员到结束的边
    return builder


def build_graph_with_memory():
    """Build and return the agent workflow graph with memory."""
    # 构建并返回带有记忆的代理工作流图
    # use persistent memory to save conversation history
    # 使用持久化内存保存对话历史
    # TODO: be compatible with SQLite / PostgreSQL
    # TODO: 兼容SQLite / PostgreSQL
    memory = MemorySaver()

    # build state graph
    # 构建状态图
    builder = _build_base_graph()
    return builder.compile(checkpointer=memory)


def build_graph():
    """Build and return the agent workflow graph without memory."""
    # 构建并返回不带记忆的代理工作流图
    # build state graph
    # 构建状态图
    builder = _build_base_graph()
    return builder.compile()


graph = build_graph()  # 创建图实例
