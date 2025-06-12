# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging

from langchain.schema import HumanMessage, SystemMessage

from src.config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_by_type
from src.prompts.template import get_prompt_template

from ..types import Script
from .state import PodcastState

logger = logging.getLogger(__name__)  # 获取日志记录器


def script_writer_node(state: PodcastState):
    """
    脚本编写节点函数
    
    使用LLM生成播客脚本
    
    参数:
        state: 播客状态对象
        
    返回:
        包含生成脚本和空音频块列表的字典
    """
    logger.info("Generating script for podcast...")  # 记录正在生成播客脚本的信息
    model = get_llm_by_type(
        AGENT_LLM_MAP["podcast_script_writer"]  # 获取播客脚本编写器的LLM类型
    ).with_structured_output(Script, method="json_mode")  # 配置LLM以生成结构化的Script输出
    script = model.invoke(
        [
            SystemMessage(content=get_prompt_template("podcast/podcast_script_writer")),  # 系统消息，包含播客脚本编写器的提示模板
            HumanMessage(content=state["input"]),  # 人类消息，包含输入内容
        ],
    )  # 调用LLM生成脚本
    print(script)  # 打印生成的脚本
    return {"script": script, "audio_chunks": []}  # 返回包含脚本和空音频块列表的字典
