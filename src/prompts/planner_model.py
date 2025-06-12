# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class StepType(str, Enum):
    """步骤类型枚举"""
    RESEARCH = "research"    # 研究类型
    PROCESSING = "processing"  # 处理类型


class Step(BaseModel):
    """计划步骤模型"""
    need_search: bool = Field(..., description="Must be explicitly set for each step")  # 是否需要搜索，必须为每个步骤明确设置
    title: str  # 标题
    description: str = Field(..., description="Specify exactly what data to collect")  # 描述，明确指定要收集的数据
    step_type: StepType = Field(..., description="Indicates the nature of the step")  # 步骤类型，表示步骤的性质
    execution_res: Optional[str] = Field(
        default=None, description="The Step execution result"  # 步骤执行结果
    )


class Plan(BaseModel):
    """计划模型"""
    locale: str = Field(
        ..., description="e.g. 'en-US' or 'zh-CN', based on the user's language"  # 区域设置，例如'en-US'或'zh-CN'，基于用户的语言
    )
    has_enough_context: bool  # 是否有足够的上下文
    thought: str  # 思考过程
    title: str  # 标题
    steps: List[Step] = Field(
        default_factory=list,
        description="Research & Processing steps to get more context",  # 获取更多上下文的研究和处理步骤
    )

    class Config:
        """配置类"""
        json_schema_extra = {
            "examples": [
                {
                    "has_enough_context": False,
                    "thought": (
                        "To understand the current market trends in AI, we need to gather comprehensive information."
                        # 为了了解AI的当前市场趋势，我们需要收集全面的信息
                    ),
                    "title": "AI Market Research Plan",  # AI市场研究计划
                    "steps": [
                        {
                            "need_search": True,
                            "title": "Current AI Market Analysis",  # 当前AI市场分析
                            "description": (
                                "Collect data on market size, growth rates, major players, and investment trends in AI sector."
                                # 收集AI行业的市场规模、增长率、主要参与者和投资趋势的数据
                            ),
                            "step_type": "research",
                        }
                    ],
                }
            ]
        }
