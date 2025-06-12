# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging

from langchain.schema import HumanMessage, SystemMessage

from src.config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_by_type
from src.prompts.template import env, apply_prompt_template
from src.prompt_enhancer.graph.state import PromptEnhancerState

logger = logging.getLogger(__name__)  # 获取日志记录器


def prompt_enhancer_node(state: PromptEnhancerState):
    """
    提示增强节点函数
    
    使用AI分析增强用户提示
    
    参数:
        state: 提示增强状态对象
        
    返回:
        包含增强后提示的字典
    """
    logger.info("Enhancing user prompt...")  # 记录正在增强用户提示的信息

    model = get_llm_by_type(AGENT_LLM_MAP["prompt_enhancer"])  # 获取提示增强器的LLM模型

    try:

        # Create messages with context if provided
        # 如果提供了上下文，则创建带有上下文的消息
        context_info = ""
        if state.get("context"):
            context_info = f"\n\nAdditional context: {state['context']}"  # 添加额外的上下文信息

        original_prompt_message = HumanMessage(
            content=f"Please enhance this prompt:{context_info}\n\nOriginal prompt: {state['prompt']}"
        )  # 创建包含原始提示和上下文的人类消息

        messages = apply_prompt_template(
            "prompt_enhancer/prompt_enhancer",
            {
                "messages": [original_prompt_message],  # 消息列表
                "report_style": state.get("report_style"),  # 报告风格
            },
        )  # 应用提示模板

        # Get the response from the model
        # 从模型获取响应
        response = model.invoke(messages)  # 调用LLM模型

        # Clean up the response - remove any extra formatting or comments
        # 清理响应 - 删除任何额外的格式或注释
        enhanced_prompt = response.content.strip()  # 去除首尾空白

        # Remove common prefixes that might be added by the model
        # 删除模型可能添加的常见前缀
        prefixes_to_remove = [
            "Enhanced Prompt:",
            "Enhanced prompt:",
            "Here's the enhanced prompt:",
            "Here is the enhanced prompt:",
            "**Enhanced Prompt**:",
            "**Enhanced prompt**:",
        ]  # 要删除的前缀列表

        for prefix in prefixes_to_remove:
            if enhanced_prompt.startswith(prefix):
                enhanced_prompt = enhanced_prompt[len(prefix) :].strip()  # 删除前缀
                break

        logger.info("Prompt enhancement completed successfully")  # 记录提示增强成功完成
        logger.debug(f"Enhanced prompt: {enhanced_prompt}")  # 记录增强后的提示
        return {"output": enhanced_prompt}  # 返回包含增强后提示的字典
    except Exception as e:
        logger.error(f"Error in prompt enhancement: {str(e)}")  # 记录提示增强错误
        return {"output": state["prompt"]}  # 如果发生错误，则返回原始提示
