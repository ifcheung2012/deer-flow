# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging

from src.podcast.graph.state import PodcastState

logger = logging.getLogger(__name__)  # 获取日志记录器


def audio_mixer_node(state: PodcastState):
    """
    音频混合节点函数
    
    将多个音频块合并为一个完整的音频文件
    
    参数:
        state: 播客状态对象
        
    返回:
        包含最终混合音频的字典
    """
    logger.info("Mixing audio chunks for podcast...")  # 记录正在混合播客音频块的信息
    audio_chunks = state["audio_chunks"]  # 获取音频块列表
    combined_audio = b"".join(audio_chunks)  # 将所有音频块连接成一个字节序列
    logger.info("The podcast audio is now ready.")  # 记录播客音频已准备就绪的信息
    return {"output": combined_audio}  # 返回包含合并音频的字典
