# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
from dataclasses import dataclass, field, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig

from src.rag.retriever import Resource
from src.config.report_style import ReportStyle


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields."""
    # 可配置的字段

    resources: list[Resource] = field(
        default_factory=list
    )  # Resources to be used for the research
      # 用于研究的资源
    max_plan_iterations: int = 1  # Maximum number of plan iterations
                                  # 计划迭代的最大次数
    max_step_num: int = 3  # Maximum number of steps in a plan
                           # 计划中步骤的最大数量
    max_search_results: int = 3  # Maximum number of search results
                                 # 搜索结果的最大数量
    mcp_settings: dict = None  # MCP settings, including dynamic loaded tools
                               # MCP设置，包括动态加载的工具
    report_style: str = ReportStyle.ACADEMIC.value  # Report style
                                                    # 报告风格

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        # 从RunnableConfig创建Configuration实例
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})
