# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import List, Optional, Union

from pydantic import BaseModel, Field

from src.rag.retriever import Resource
from src.config.report_style import ReportStyle


class ContentItem(BaseModel):
    """内容项模型，表示消息中的一个内容元素"""
    type: str = Field(..., description="The type of content (text, image, etc.)")  # 内容类型（文本、图像等）
    text: Optional[str] = Field(None, description="The text content if type is 'text'")  # 如果类型是'text'，则为文本内容
    image_url: Optional[str] = Field(
        None, description="The image URL if type is 'image'"  # 如果类型是'image'，则为图像URL
    )


class ChatMessage(BaseModel):
    """聊天消息模型，表示一条聊天消息"""
    role: str = Field(
        ..., description="The role of the message sender (user or assistant)"  # 消息发送者的角色（用户或助手）
    )
    content: Union[str, List[ContentItem]] = Field(
        ...,
        description="The content of the message, either a string or a list of content items",  # 消息内容，可以是字符串或内容项列表
    )


class ChatRequest(BaseModel):
    """聊天请求模型，表示一个完整的聊天请求"""
    messages: Optional[List[ChatMessage]] = Field(
        [], description="History of messages between the user and the assistant"  # 用户和助手之间的消息历史
    )
    resources: Optional[List[Resource]] = Field(
        [], description="Resources to be used for the research"  # 用于研究的资源
    )
    debug: Optional[bool] = Field(False, description="Whether to enable debug logging")  # 是否启用调试日志
    thread_id: Optional[str] = Field(
        "__default__", description="A specific conversation identifier"  # 特定的对话标识符
    )
    max_plan_iterations: Optional[int] = Field(
        1, description="The maximum number of plan iterations"  # 计划迭代的最大次数
    )
    max_step_num: Optional[int] = Field(
        3, description="The maximum number of steps in a plan"  # 计划中步骤的最大数量
    )
    max_search_results: Optional[int] = Field(
        3, description="The maximum number of search results"  # 搜索结果的最大数量
    )
    auto_accepted_plan: Optional[bool] = Field(
        False, description="Whether to automatically accept the plan"  # 是否自动接受计划
    )
    interrupt_feedback: Optional[str] = Field(
        None, description="Interrupt feedback from the user on the plan"  # 用户对计划的中断反馈
    )
    mcp_settings: Optional[dict] = Field(
        None, description="MCP settings for the chat request"  # 聊天请求的MCP设置
    )
    enable_background_investigation: Optional[bool] = Field(
        True, description="Whether to get background investigation before plan"  # 是否在计划前进行背景调查
    )
    report_style: Optional[ReportStyle] = Field(
        ReportStyle.ACADEMIC, description="The style of the report"  # 报告的风格
    )


class TTSRequest(BaseModel):
    """文本转语音请求模型"""
    text: str = Field(..., description="The text to convert to speech")  # 要转换为语音的文本
    voice_type: Optional[str] = Field(
        "BV700_V2_streaming", description="The voice type to use"  # 要使用的语音类型
    )
    encoding: Optional[str] = Field("mp3", description="The audio encoding format")  # 音频编码格式
    speed_ratio: Optional[float] = Field(1.0, description="Speech speed ratio")  # 语音速度比率
    volume_ratio: Optional[float] = Field(1.0, description="Speech volume ratio")  # 语音音量比率
    pitch_ratio: Optional[float] = Field(1.0, description="Speech pitch ratio")  # 语音音调比率
    text_type: Optional[str] = Field("plain", description="Text type (plain or ssml)")  # 文本类型（普通文本或SSML）
    with_frontend: Optional[int] = Field(
        1, description="Whether to use frontend processing"  # 是否使用前端处理
    )
    frontend_type: Optional[str] = Field("unitTson", description="Frontend type")  # 前端类型


class GeneratePodcastRequest(BaseModel):
    """生成播客请求模型"""
    content: str = Field(..., description="The content of the podcast")  # 播客的内容


class GeneratePPTRequest(BaseModel):
    """生成PPT请求模型"""
    content: str = Field(..., description="The content of the ppt")  # PPT的内容


class GenerateProseRequest(BaseModel):
    """生成散文请求模型"""
    prompt: str = Field(..., description="The content of the prose")  # 散文的内容
    option: str = Field(..., description="The option of the prose writer")  # 散文作者的选项
    command: Optional[str] = Field(
        "", description="The user custom command of the prose writer"  # 散文作者的用户自定义命令
    )


class EnhancePromptRequest(BaseModel):
    """增强提示请求模型"""
    prompt: str = Field(..., description="The original prompt to enhance")  # 要增强的原始提示
    context: Optional[str] = Field(
        "", description="Additional context about the intended use"  # 关于预期用途的额外上下文
    )
    report_style: Optional[str] = Field(
        "academic", description="The style of the report"  # 报告的风格
    )
