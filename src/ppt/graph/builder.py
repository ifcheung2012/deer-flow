# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import END, START, StateGraph

from src.ppt.graph.ppt_composer_node import ppt_composer_node
from src.ppt.graph.ppt_generator_node import ppt_generator_node
from src.ppt.graph.state import PPTState


def build_graph():
    """
    构建并返回PPT工作流图
    
    返回:
        编译后的PPT工作流图
    """
    # build state graph
    # 构建状态图
    builder = StateGraph(PPTState)  # 创建状态图构建器，使用PPTState作为状态类型
    builder.add_node("ppt_composer", ppt_composer_node)  # 添加PPT内容组合节点
    builder.add_node("ppt_generator", ppt_generator_node)  # 添加PPT生成节点
    builder.add_edge(START, "ppt_composer")  # 从开始节点连接到PPT内容组合节点
    builder.add_edge("ppt_composer", "ppt_generator")  # 从PPT内容组合节点连接到PPT生成节点
    builder.add_edge("ppt_generator", END)  # 从PPT生成节点连接到结束节点
    return builder.compile()  # 编译并返回工作流图


workflow = build_graph()  # 构建工作流图

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()  # 加载环境变量

    report_content = open("examples/nanjing_tangbao.md").read()  # 读取报告内容
    final_state = workflow.invoke({"input": report_content})  # 调用工作流
