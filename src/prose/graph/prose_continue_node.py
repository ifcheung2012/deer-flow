# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging

from langchain.schema import HumanMessage, SystemMessage

from src.config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_by_type
from src.prompts.template import get_prompt_template
from src.prose.graph.state import ProseState

logger = logging.getLogger(__name__)  # 获取日志记录器


def prose_continue_node(state: ProseState):
    """
    散文继续写作节点函数
    
    使用LLM继续现有散文内容
    
    参数:
        state: 散文状态对象
        
    返回:
        包含生成的散文输出的字典
    """
    logger.info("Generating prose continue content...")  # 记录正在生成散文继续内容的信息
    model = get_llm_by_type(AGENT_LLM_MAP["prose_writer"])  # 获取散文写作器的LLM模型
    prose_content = model.invoke(
        [
            SystemMessage(content=get_prompt_template("prose/prose_continue")),  # 系统消息，包含散文继续写作的提示模板
            HumanMessage(content=state["content"]),  # 人类消息，包含当前散文内容
        ],
    )  # 调用LLM生成散文继续内容
    return {"output": prose_content.content}  # 返回包含生成的散文输出的字典
