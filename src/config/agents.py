# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Literal

# Define available LLM types
# 定义可用的LLM类型
LLMType = Literal["basic", "reasoning", "vision"]

# Define agent-LLM mapping
# 定义代理-LLM映射
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "basic",  # 协调员
    "planner": "basic",      # 规划员
    "researcher": "basic",   # 研究员
    "coder": "basic",        # 编码员
    "reporter": "basic",     # 报告员
    "podcast_script_writer": "basic",  # 播客脚本作者
    "ppt_composer": "basic",           # PPT作曲家
    "prose_writer": "basic",           # 散文作者
    "prompt_enhancer": "basic",        # 提示增强器
}
