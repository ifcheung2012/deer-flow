# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import StateGraph

from src.prompt_enhancer.graph.enhancer_node import prompt_enhancer_node
from src.prompt_enhancer.graph.state import PromptEnhancerState


def build_graph():
    """
    构建并返回提示增强工作流图
    
    返回:
        编译后的提示增强工作流图
    """
    # Build state graph
    # 构建状态图
    builder = StateGraph(PromptEnhancerState)  # 创建状态图构建器，使用PromptEnhancerState作为状态类型

    # Add the enhancer node
    # 添加增强器节点
    builder.add_node("enhancer", prompt_enhancer_node)  # 添加提示增强节点

    # Set entry point
    # 设置入口点
    builder.set_entry_point("enhancer")  # 将增强器节点设置为入口点

    # Set finish point
    # 设置结束点
    builder.set_finish_point("enhancer")  # 将增强器节点设置为结束点

    # Compile and return the graph
    # 编译并返回图
    return builder.compile()  # 编译并返回工作流图
