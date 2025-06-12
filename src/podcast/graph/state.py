# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Optional

from langgraph.graph import MessagesState

from ..types import Script


class PodcastState(MessagesState):
    """
    播客生成的状态类
    
    继承自MessagesState，用于在播客生成工作流中传递状态
    """

    # Input
    # 输入
    input: str = ""  # 输入文本

    # Output
    # 输出
    output: Optional[bytes] = None  # 最终输出的音频字节数据

    # Assets
    # 资源
    script: Optional[Script] = None  # 生成的脚本
    audio_chunks: list[bytes] = []  # 音频块列表
