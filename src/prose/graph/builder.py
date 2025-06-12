# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import asyncio
import logging
from langgraph.graph import END, START, StateGraph

from src.prose.graph.prose_continue_node import prose_continue_node
from src.prose.graph.prose_fix_node import prose_fix_node
from src.prose.graph.prose_improve_node import prose_improve_node
from src.prose.graph.prose_longer_node import prose_longer_node
from src.prose.graph.prose_shorter_node import prose_shorter_node
from src.prose.graph.prose_zap_node import prose_zap_node
from src.prose.graph.state import ProseState


def optional_node(state: ProseState):
    """
    条件路由函数，根据状态中的选项决定下一个节点
    
    参数:
        state: 散文状态对象
        
    返回:
        选项字符串，用于条件路由
    """
    return state["option"]  # 返回状态中的选项


def build_graph():
    """
    构建并返回散文工作流图
    
    返回:
        编译后的散文工作流图
    """
    # build state graph
    # 构建状态图
    builder = StateGraph(ProseState)  # 创建状态图构建器，使用ProseState作为状态类型
    builder.add_node("prose_continue", prose_continue_node)  # 添加继续写作节点
    builder.add_node("prose_improve", prose_improve_node)  # 添加改进节点
    builder.add_node("prose_shorter", prose_shorter_node)  # 添加缩短节点
    builder.add_node("prose_longer", prose_longer_node)  # 添加延长节点
    builder.add_node("prose_fix", prose_fix_node)  # 添加修复节点
    builder.add_node("prose_zap", prose_zap_node)  # 添加重写节点
    builder.add_conditional_edges(
        START,  # 开始节点
        optional_node,  # 条件路由函数
        {
            "continue": "prose_continue",  # 如果选项是"continue"，则路由到继续写作节点
            "improve": "prose_improve",  # 如果选项是"improve"，则路由到改进节点
            "shorter": "prose_shorter",  # 如果选项是"shorter"，则路由到缩短节点
            "longer": "prose_longer",  # 如果选项是"longer"，则路由到延长节点
            "fix": "prose_fix",  # 如果选项是"fix"，则路由到修复节点
            "zap": "prose_zap",  # 如果选项是"zap"，则路由到重写节点
        },
        END,  # 结束节点
    )  # 添加条件边，根据选项决定路由到哪个节点
    return builder.compile()  # 编译并返回工作流图


async def _test_workflow():
    """
    测试工作流的异步函数
    """
    workflow = build_graph()  # 构建工作流图
    events = workflow.astream(
        {
            "content": "The weather in Beijing is sunny",  # 初始内容
            "option": "continue",  # 选项为继续写作
        },
        stream_mode="messages",
        subgraphs=True,
    )  # 异步流式调用工作流
    async for node, event in events:
        e = event[0]  # 获取事件
        print({"id": e.id, "object": "chat.completion.chunk", "content": e.content})  # 打印事件内容


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()  # 加载环境变量
    logging.basicConfig(level=logging.INFO)  # 配置日志级别
    asyncio.run(_test_workflow())  # 运行测试工作流
