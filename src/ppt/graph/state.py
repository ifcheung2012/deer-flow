# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Optional

from langgraph.graph import MessagesState


class PPTState(MessagesState):
    """
    PPT生成的状态类
    
    继承自MessagesState，用于在PPT生成工作流中传递状态
    """

    # Input
    # 输入
    input: str = ""  # 输入文本

    # Output
    # 输出
    generated_file_path: str = ""  # 生成的PPT文件路径

    # Assets
    # 资源
    ppt_content: str = ""  # PPT内容
    ppt_file_path: str = ""  # PPT文件路径
