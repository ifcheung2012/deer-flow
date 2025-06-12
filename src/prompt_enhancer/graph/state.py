# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import TypedDict, Optional
from src.config.report_style import ReportStyle


class PromptEnhancerState(TypedDict):
    """
    提示增强工作流的状态类
    
    用于在提示增强工作流中传递状态
    """

    prompt: str  # Original prompt to enhance  # 要增强的原始提示
    context: Optional[str]  # Additional context  # 额外的上下文
    report_style: Optional[ReportStyle]  # Report style preference  # 报告风格偏好
    output: Optional[str]  # Enhanced prompt result  # 增强后的提示结果
