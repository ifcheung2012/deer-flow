# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Text-to-Speech module using volcengine TTS API.
"""
# 使用火山引擎TTS API的文本转语音模块

import json
import uuid
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)  # 获取日志记录器


class VolcengineTTS:
    """
    Client for volcengine Text-to-Speech API.
    """
    # 火山引擎文本转语音API的客户端

    def __init__(
        self,
        appid: str,
        access_token: str,
        cluster: str = "volcano_tts",
        voice_type: str = "BV700_V2_streaming",
        host: str = "openspeech.bytedance.com",
    ):
        """
        Initialize the volcengine TTS client.

        Args:
            appid: Platform application ID
            access_token: Access token for authentication
            cluster: TTS cluster name
            voice_type: Voice type to use
            host: API host
        """
        # 初始化火山引擎TTS客户端
        #
        # 参数:
        #     appid: 平台应用ID
        #     access_token: 用于认证的访问令牌
        #     cluster: TTS集群名称
        #     voice_type: 要使用的语音类型
        #     host: API主机
        
        self.appid = appid
        self.access_token = access_token
        self.cluster = cluster
        self.voice_type = voice_type
        self.host = host
        self.api_url = f"https://{host}/api/v1/tts"  # API URL
        self.header = {"Authorization": f"Bearer;{access_token}"}  # 认证头

    def text_to_speech(
        self,
        text: str,
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
        volume_ratio: float = 1.0,
        pitch_ratio: float = 1.0,
        text_type: str = "plain",
        with_frontend: int = 1,
        frontend_type: str = "unitTson",
        uid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convert text to speech using volcengine TTS API.

        Args:
            text: Text to convert to speech
            encoding: Audio encoding format
            speed_ratio: Speech speed ratio
            volume_ratio: Speech volume ratio
            pitch_ratio: Speech pitch ratio
            text_type: Text type (plain or ssml)
            with_frontend: Whether to use frontend processing
            frontend_type: Frontend type
            uid: User ID (generated if not provided)

        Returns:
            Dictionary containing the API response and base64-encoded audio data
        """
        # 使用火山引擎TTS API将文本转换为语音
        #
        # 参数:
        #     text: 要转换为语音的文本
        #     encoding: 音频编码格式
        #     speed_ratio: 语音速度比率
        #     volume_ratio: 语音音量比率
        #     pitch_ratio: 语音音调比率
        #     text_type: 文本类型（plain或ssml）
        #     with_frontend: 是否使用前端处理
        #     frontend_type: 前端类型
        #     uid: 用户ID（如果未提供则生成）
        #
        # 返回:
        #     包含API响应和base64编码的音频数据的字典
        
        if not uid:
            uid = str(uuid.uuid4())  # 生成唯一ID

        request_json = {
            "app": {
                "appid": self.appid,
                "token": self.access_token,
                "cluster": self.cluster,
            },
            "user": {"uid": uid},
            "audio": {
                "voice_type": self.voice_type,
                "encoding": encoding,
                "speed_ratio": speed_ratio,
                "volume_ratio": volume_ratio,
                "pitch_ratio": pitch_ratio,
            },
            "request": {
                "reqid": str(uuid.uuid4()),  # 请求ID
                "text": text,
                "text_type": text_type,
                "operation": "query",
                "with_frontend": with_frontend,
                "frontend_type": frontend_type,
            },
        }

        try:
            sanitized_text = text.replace("\r\n", "").replace("\n", "")  # 清理文本
            logger.debug(f"Sending TTS request for text: {sanitized_text[:50]}...")  # 发送TTS请求
            response = requests.post(
                self.api_url, json.dumps(request_json), headers=self.header
            )
            response_json = response.json()

            if response.status_code != 200:
                logger.error(f"TTS API error: {response_json}")  # TTS API错误
                return {"success": False, "error": response_json, "audio_data": None}

            if "data" not in response_json:
                logger.error(f"TTS API returned no data: {response_json}")  # TTS API未返回数据
                return {
                    "success": False,
                    "error": "No audio data returned",  # 未返回音频数据
                    "audio_data": None,
                }

            return {
                "success": True,
                "response": response_json,
                "audio_data": response_json["data"],  # Base64编码的音频数据
            }

        except Exception as e:
            logger.exception(f"Error in TTS API call: {str(e)}")  # TTS API调用错误
            return {"success": False, "error": str(e), "audio_data": None}
