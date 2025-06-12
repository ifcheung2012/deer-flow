# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import MessagesState


class ProseState(MessagesState):
    """
    散文生成的状态类
    
    继承自MessagesState，用于在散文生成工作流中传递状态
    """

    # The content of the prose
    # 散文的内容
    content: str = ""  # 散文内容

    # Prose writer option: continue, improve, shorter, longer, fix, zap
    # 散文写作选项：继续、改进、缩短、延长、修复、重写
    option: str = ""  # 选项

    # The user custom command for the prose writer
    # 用户为散文写作器提供的自定义命令
    command: str = ""  # 自定义命令

    # Output
    # 输出
    output: str = ""  # 输出内容
