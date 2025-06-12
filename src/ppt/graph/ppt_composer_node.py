# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os
import uuid

from langchain.schema import HumanMessage, SystemMessage

from src.config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_by_type
from src.prompts.template import get_prompt_template

from .state import PPTState

logger = logging.getLogger(__name__)  # 获取日志记录器


def ppt_composer_node(state: PPTState):
    """
    PPT内容组合节点函数
    
    使用LLM生成PPT内容
    
    参数:
        state: PPT状态对象
        
    返回:
        包含PPT内容和临时文件路径的字典
    """
    logger.info("Generating ppt content...")  # 记录正在生成PPT内容的信息
    model = get_llm_by_type(AGENT_LLM_MAP["ppt_composer"])  # 获取PPT内容组合器的LLM模型
    ppt_content = model.invoke(
        [
            SystemMessage(content=get_prompt_template("ppt/ppt_composer")),  # 系统消息，包含PPT内容组合器的提示模板
            HumanMessage(content=state["input"]),  # 人类消息，包含输入内容
        ],
    )  # 调用LLM生成PPT内容
    logger.info(f"ppt_content: {ppt_content}")  # 记录生成的PPT内容
    # save the ppt content in a temp file
    # 将PPT内容保存到临时文件
    temp_ppt_file_path = os.path.join(os.getcwd(), f"ppt_content_{uuid.uuid4()}.md")  # 创建临时文件路径
    with open(temp_ppt_file_path, "w") as f:
        f.write(ppt_content.content)  # 将PPT内容写入临时文件
    return {"ppt_content": ppt_content, "ppt_file_path": temp_ppt_file_path}  # 返回包含PPT内容和临时文件路径的字典
