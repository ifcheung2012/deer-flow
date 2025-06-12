# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import base64
import logging
import os

from src.podcast.graph.state import PodcastState
from src.tools.tts import VolcengineTTS

logger = logging.getLogger(__name__)  # 获取日志记录器


def tts_node(state: PodcastState):
    """
    文本转语音节点函数
    
    将脚本中的每一行文本转换为语音
    
    参数:
        state: 播客状态对象
        
    返回:
        包含音频块列表的字典
    """
    logger.info("Generating audio chunks for podcast...")  # 记录正在生成播客音频块的信息
    tts_client = _create_tts_client()  # 创建TTS客户端
    for line in state["script"].lines:
        tts_client.voice_type = (
            "BV002_streaming" if line.speaker == "male" else "BV001_streaming"
        )  # 根据说话者性别设置语音类型，男性使用BV002，女性使用BV001
        result = tts_client.text_to_speech(line.paragraph, speed_ratio=1.05)  # 调用TTS API将文本转换为语音，语速稍快
        if result["success"]:
            audio_data = result["audio_data"]  # 获取音频数据
            audio_chunk = base64.b64decode(audio_data)  # 解码base64音频数据
            state["audio_chunks"].append(audio_chunk)  # 将音频块添加到状态中
        else:
            logger.error(result["error"])  # 记录错误信息
    return {
        "audio_chunks": state["audio_chunks"],  # 返回音频块列表
    }


def _create_tts_client():
    """
    创建TTS客户端
    
    从环境变量获取配置并创建火山引擎TTS客户端
    
    返回:
        VolcengineTTS客户端实例
    """
    app_id = os.getenv("VOLCENGINE_TTS_APPID", "")  # 获取火山引擎TTS应用ID
    if not app_id:
        raise Exception("VOLCENGINE_TTS_APPID is not set")  # 如果应用ID未设置，抛出异常
    access_token = os.getenv("VOLCENGINE_TTS_ACCESS_TOKEN", "")  # 获取火山引擎TTS访问令牌
    if not access_token:
        raise Exception("VOLCENGINE_TTS_ACCESS_TOKEN is not set")  # 如果访问令牌未设置，抛出异常
    cluster = os.getenv("VOLCENGINE_TTS_CLUSTER", "volcano_tts")  # 获取火山引擎TTS集群
    voice_type = "BV001_streaming"  # 默认语音类型为女性
    return VolcengineTTS(
        appid=app_id,
        access_token=access_token,
        cluster=cluster,
        voice_type=voice_type,
    )  # 返回火山引擎TTS客户端实例
