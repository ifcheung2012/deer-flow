# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import dataclasses
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langgraph.prebuilt.chat_agent_executor import AgentState
from src.config.configuration import Configuration

# Initialize Jinja2 environment
# 初始化Jinja2环境
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),  # 从当前文件目录加载模板
    autoescape=select_autoescape(),  # 自动转义
    trim_blocks=True,  # 删除块后的第一个换行符
    lstrip_blocks=True,  # 删除块前的空白
)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    # 使用Jinja2加载并返回提示模板
    #
    # 参数:
    #     prompt_name: 提示模板文件名（不带.md扩展名）
    #
    # 返回:
    #     带有适当变量替换语法的模板字符串
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")  # 加载模板错误


def apply_prompt_template(
    prompt_name: str, state: AgentState, configurable: Configuration = None
) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute

    Returns:
        List of messages with the system prompt as the first message
    """
    # 将模板变量应用于提示模板并返回格式化的消息
    #
    # 参数:
    #     prompt_name: 要使用的提示模板名称
    #     state: 包含要替换变量的当前代理状态
    #     configurable: 配置对象
    #
    # 返回:
    #     消息列表，系统提示作为第一条消息
    
    # Convert state to dict for template rendering
    # 将状态转换为字典用于模板渲染
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),  # 当前时间
        **state,
    }

    # Add configurable variables
    # 添加可配置变量
    if configurable:
        state_vars.update(dataclasses.asdict(configurable))

    try:
        template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")  # 应用模板错误
