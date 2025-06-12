# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from .tools import SELECTED_SEARCH_ENGINE, SearchEngine
from .loader import load_yaml_config
from .questions import BUILT_IN_QUESTIONS, BUILT_IN_QUESTIONS_ZH_CN

from dotenv import load_dotenv

# Load environment variables
# 加载环境变量
load_dotenv()

# Team configuration
# 团队配置
TEAM_MEMBER_CONFIGRATIONS = {
    "researcher": {
        "name": "researcher",  # 研究员
        "desc": (
            "Responsible for searching and collecting relevant information, understanding user needs and conducting research analysis"
            # 负责搜索和收集相关信息，理解用户需求并进行研究分析
        ),
        "desc_for_llm": (
            "Uses search engines and web crawlers to gather information from the internet. "
            "Outputs a Markdown report summarizing findings. Researcher can not do math or programming."
            # 使用搜索引擎和网络爬虫从互联网收集信息。
            # 输出一个总结发现的Markdown报告。研究员不能进行数学计算或编程。
        ),
        "is_optional": False,  # 不可选的
    },
    "coder": {
        "name": "coder",  # 编码员
        "desc": (
            "Responsible for code implementation, debugging and optimization, handling technical programming tasks"
            # 负责代码实现、调试和优化，处理技术编程任务
        ),
        "desc_for_llm": (
            "Executes Python or Bash commands, performs mathematical calculations, and outputs a Markdown report. "
            "Must be used for all mathematical computations."
            # 执行Python或Bash命令，进行数学计算，并输出Markdown报告。
            # 必须用于所有数学计算。
        ),
        "is_optional": True,  # 可选的
    },
}

TEAM_MEMBERS = list(TEAM_MEMBER_CONFIGRATIONS.keys())  # 团队成员列表

__all__ = [
    # Other configurations
    # 其他配置
    "TEAM_MEMBERS",
    "TEAM_MEMBER_CONFIGRATIONS",
    "SELECTED_SEARCH_ENGINE",
    "SearchEngine",
    "BUILT_IN_QUESTIONS",
    "BUILT_IN_QUESTIONS_ZH_CN",
]
