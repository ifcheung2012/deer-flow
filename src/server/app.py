# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import base64
import json
import logging
import os
from typing import Annotated, List, cast
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from langchain_core.messages import AIMessageChunk, ToolMessage, BaseMessage
from langgraph.types import Command

from src.config.report_style import ReportStyle
from src.config.tools import SELECTED_RAG_PROVIDER
from src.graph.builder import build_graph_with_memory
from src.podcast.graph.builder import build_graph as build_podcast_graph
from src.ppt.graph.builder import build_graph as build_ppt_graph
from src.prose.graph.builder import build_graph as build_prose_graph
from src.prompt_enhancer.graph.builder import build_graph as build_prompt_enhancer_graph
from src.rag.builder import build_retriever
from src.rag.retriever import Resource
from src.server.chat_request import (
    ChatMessage,
    ChatRequest,
    EnhancePromptRequest,
    GeneratePodcastRequest,
    GeneratePPTRequest,
    GenerateProseRequest,
    TTSRequest,
)
from src.server.mcp_request import MCPServerMetadataRequest, MCPServerMetadataResponse
from src.server.mcp_utils import load_mcp_tools
from src.server.rag_request import (
    RAGConfigResponse,
    RAGResourceRequest,
    RAGResourcesResponse,
)
from src.tools import VolcengineTTS

logger = logging.getLogger(__name__)  # 获取日志记录器

INTERNAL_SERVER_ERROR_DETAIL = "Internal Server Error"  # 内部服务器错误详情

app = FastAPI(
    title="DeerFlow API",
    description="API for Deer",
    version="0.1.0",
)  # 创建FastAPI应用实例

# Add CORS middleware
# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods 允许所有方法
    allow_headers=["*"],  # Allows all headers 允许所有头部
)

graph = build_graph_with_memory()  # 构建带有记忆的图


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    聊天流API端点，用于流式处理聊天请求
    
    参数:
        request: 聊天请求对象
        
    返回:
        流式响应，包含聊天事件流
    """
    thread_id = request.thread_id
    if thread_id == "__default__":
        thread_id = str(uuid4())  # 如果线程ID是默认值，则生成一个新的UUID
    return StreamingResponse(
        _astream_workflow_generator(
            request.model_dump()["messages"],  # 消息
            thread_id,  # 线程ID
            request.resources,  # 资源
            request.max_plan_iterations,  # 最大计划迭代次数
            request.max_step_num,  # 最大步骤数
            request.max_search_results,  # 最大搜索结果数
            request.auto_accepted_plan,  # 自动接受计划
            request.interrupt_feedback,  # 中断反馈
            request.mcp_settings,  # MCP设置
            request.enable_background_investigation,  # 启用背景调查
            request.report_style,  # 报告风格
        ),
        media_type="text/event-stream",  # 媒体类型为事件流
    )


async def _astream_workflow_generator(
    messages: List[dict],
    thread_id: str,
    resources: List[Resource],
    max_plan_iterations: int,
    max_step_num: int,
    max_search_results: int,
    auto_accepted_plan: bool,
    interrupt_feedback: str,
    mcp_settings: dict,
    enable_background_investigation: bool,
    report_style: ReportStyle,
):
    """
    异步工作流生成器，用于生成聊天事件流
    
    参数:
        messages: 消息列表
        thread_id: 线程ID
        resources: 资源列表
        max_plan_iterations: 最大计划迭代次数
        max_step_num: 最大步骤数
        max_search_results: 最大搜索结果数
        auto_accepted_plan: 是否自动接受计划
        interrupt_feedback: 中断反馈
        mcp_settings: MCP设置
        enable_background_investigation: 是否启用背景调查
        report_style: 报告风格
        
    生成:
        聊天事件流
    """
    input_ = {
        "messages": messages,  # 消息
        "plan_iterations": 0,  # 计划迭代次数
        "final_report": "",  # 最终报告
        "current_plan": None,  # 当前计划
        "observations": [],  # 观察结果
        "auto_accepted_plan": auto_accepted_plan,  # 自动接受计划
        "enable_background_investigation": enable_background_investigation,  # 启用背景调查
        "research_topic": messages[-1]["content"] if messages else "",  # 研究主题
    }
    if not auto_accepted_plan and interrupt_feedback:
        # 如果不是自动接受计划且有中断反馈
        resume_msg = f"[{interrupt_feedback}]"  # 恢复消息
        # add the last message to the resume message
        # 将最后一条消息添加到恢复消息中
        if messages:
            resume_msg += f" {messages[-1]['content']}"
        input_ = Command(resume=resume_msg)  # 创建恢复命令
    async for agent, _, event_data in graph.astream(
        input_,
        config={
            "thread_id": thread_id,
            "resources": resources,
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num,
            "max_search_results": max_search_results,
            "mcp_settings": mcp_settings,
            "report_style": report_style.value,
        },
        stream_mode=["messages", "updates"],
        subgraphs=True,
    ):
        # 处理事件数据
        if isinstance(event_data, dict):
            if "__interrupt__" in event_data:
                # 如果是中断事件
                yield _make_event(
                    "interrupt",
                    {
                        "thread_id": thread_id,
                        "id": event_data["__interrupt__"][0].ns[0],
                        "role": "assistant",
                        "content": event_data["__interrupt__"][0].value,
                        "finish_reason": "interrupt",
                        "options": [
                            {"text": "Edit plan", "value": "edit_plan"},  # 编辑计划选项
                            {"text": "Start research", "value": "accepted"},  # 开始研究选项
                        ],
                    },
                )
            continue
        message_chunk, message_metadata = cast(
            tuple[BaseMessage, dict[str, any]], event_data
        )
        event_stream_message: dict[str, any] = {
            "thread_id": thread_id,
            "agent": agent[0].split(":")[0],  # 代理名称
            "id": message_chunk.id,  # 消息ID
            "role": "assistant",  # 角色
            "content": message_chunk.content,  # 内容
        }
        if message_chunk.response_metadata.get("finish_reason"):
            # 如果有完成原因
            event_stream_message["finish_reason"] = message_chunk.response_metadata.get(
                "finish_reason"
            )
        if isinstance(message_chunk, ToolMessage):
            # Tool Message - Return the result of the tool call
            # 工具消息 - 返回工具调用结果
            event_stream_message["tool_call_id"] = message_chunk.tool_call_id  # 工具调用ID
            yield _make_event("tool_call_result", event_stream_message)  # 生成工具调用结果事件
        elif isinstance(message_chunk, AIMessageChunk):
            # AI Message - Raw message tokens
            # AI消息 - 原始消息令牌
            if message_chunk.tool_calls:
                # AI Message - Tool Call
                # AI消息 - 工具调用
                event_stream_message["tool_calls"] = message_chunk.tool_calls  # 工具调用
                event_stream_message["tool_call_chunks"] = (
                    message_chunk.tool_call_chunks  # 工具调用块
                )
                yield _make_event("tool_calls", event_stream_message)  # 生成工具调用事件
            elif message_chunk.tool_call_chunks:
                # AI Message - Tool Call Chunks
                # AI消息 - 工具调用块
                event_stream_message["tool_call_chunks"] = (
                    message_chunk.tool_call_chunks  # 工具调用块
                )
                yield _make_event("tool_call_chunks", event_stream_message)  # 生成工具调用块事件
            else:
                # AI Message - Raw message tokens
                # AI消息 - 原始消息令牌
                yield _make_event("message_chunk", event_stream_message)  # 生成消息块事件


def _make_event(event_type: str, data: dict[str, any]):
    """
    创建事件流消息
    
    参数:
        event_type: 事件类型
        data: 事件数据
        
    返回:
        格式化的事件流消息
    """
    if data.get("content") == "":
        data.pop("content")  # 如果内容为空，则移除内容字段
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"  # 返回格式化的事件流消息


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using volcengine TTS API."""
    # 使用火山引擎TTS API将文本转换为语音
    try:
        app_id = os.getenv("VOLCENGINE_TTS_APPID", "")  # 获取火山引擎TTS应用ID
        if not app_id:
            raise HTTPException(
                status_code=400, detail="VOLCENGINE_TTS_APPID is not set"  # 火山引擎TTS应用ID未设置
            )
        access_token = os.getenv("VOLCENGINE_TTS_ACCESS_TOKEN", "")  # 获取火山引擎TTS访问令牌
        if not access_token:
            raise HTTPException(
                status_code=400, detail="VOLCENGINE_TTS_ACCESS_TOKEN is not set"  # 火山引擎TTS访问令牌未设置
            )
        cluster = os.getenv("VOLCENGINE_TTS_CLUSTER", "volcano_tts")  # 获取火山引擎TTS集群
        voice_type = os.getenv("VOLCENGINE_TTS_VOICE_TYPE", "BV700_V2_streaming")  # 获取火山引擎TTS语音类型

        tts_client = VolcengineTTS(
            appid=app_id,
            access_token=access_token,
            cluster=cluster,
            voice_type=voice_type,
        )  # 创建火山引擎TTS客户端
        # Call the TTS API
        # 调用TTS API
        result = tts_client.text_to_speech(
            text=request.text[:1024],  # 限制文本长度为1024
            encoding=request.encoding,  # 编码格式
            speed_ratio=request.speed_ratio,  # 语速比例
            volume_ratio=request.volume_ratio,  # 音量比例
            pitch_ratio=request.pitch_ratio,  # 音调比例
            text_type=request.text_type,  # 文本类型
            with_frontend=request.with_frontend,  # 是否使用前端处理
            frontend_type=request.frontend_type,  # 前端处理类型
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=str(result["error"]))  # 如果TTS调用失败，抛出异常

        # Decode the base64 audio data
        # 解码base64音频数据
        audio_data = base64.b64decode(result["audio_data"])

        # Return the audio file
        # 返回音频文件
        return Response(
            content=audio_data,
            media_type=f"audio/{request.encoding}",
            headers={
                "Content-Disposition": (
                    f"attachment; filename=tts_output.{request.encoding}"  # 设置文件名
                )
            },
        )
    except Exception as e:
        logger.exception(f"Error in TTS endpoint: {str(e)}")  # 记录TTS端点错误
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)  # 抛出内部服务器错误


@app.post("/api/podcast/generate")
async def generate_podcast(request: GeneratePodcastRequest):
    """
    生成播客API端点
    
    参数:
        request: 生成播客请求对象
        
    返回:
        音频响应，包含生成的播客
    """
    try:
        report_content = request.content  # 获取报告内容
        print(report_content)  # 打印报告内容
        workflow = build_podcast_graph()  # 构建播客图
        final_state = workflow.invoke({"input": report_content})  # 调用工作流
        audio_bytes = final_state["output"]  # 获取音频字节
        return Response(content=audio_bytes, media_type="audio/mp3")  # 返回MP3格式的音频响应
    except Exception as e:
        logger.exception(f"Error occurred during podcast generation: {str(e)}")  # 记录播客生成错误
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)  # 抛出内部服务器错误


@app.post("/api/ppt/generate")
async def generate_ppt(request: GeneratePPTRequest):
    """
    生成PPT API端点
    
    参数:
        request: 生成PPT请求对象
        
    返回:
        PPT文件响应
    """
    try:
        report_content = request.content  # 获取报告内容
        print(report_content)  # 打印报告内容
        workflow = build_ppt_graph()  # 构建PPT图
        final_state = workflow.invoke({"input": report_content})  # 调用工作流
        generated_file_path = final_state["generated_file_path"]  # 获取生成的文件路径
        with open(generated_file_path, "rb") as f:
            ppt_bytes = f.read()  # 读取PPT文件字节
        return Response(
            content=ppt_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",  # PPT文件的MIME类型
        )
    except Exception as e:
        logger.exception(f"Error occurred during ppt generation: {str(e)}")  # 记录PPT生成错误
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)  # 抛出内部服务器错误


@app.post("/api/prose/generate")
async def generate_prose(request: GenerateProseRequest):
    """
    生成散文API端点
    
    参数:
        request: 生成散文请求对象
        
    返回:
        流式响应，包含生成的散文
    """
    try:
        sanitized_prompt = request.prompt.replace("\r\n", "").replace("\n", "")  # 清理提示，移除换行符
        logger.info(f"Generating prose for prompt: {sanitized_prompt}")  # 记录生成散文的提示
        workflow = build_prose_graph()  # 构建散文图
        events = workflow.astream(
            {
                "content": request.prompt,  # 内容
                "option": request.option,  # 选项
                "command": request.command,  # 命令
            },
            stream_mode="messages",
            subgraphs=True,
        )  # 异步流式调用工作流
        return StreamingResponse(
            (f"data: {event[0].content}\n\n" async for _, event in events),  # 生成事件流
            media_type="text/event-stream",  # 媒体类型为事件流
        )
    except Exception as e:
        logger.exception(f"Error occurred during prose generation: {str(e)}")  # 记录散文生成错误
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)  # 抛出内部服务器错误


@app.post("/api/prompt/enhance")
async def enhance_prompt(request: EnhancePromptRequest):
    """
    增强提示API端点
    
    参数:
        request: 增强提示请求对象
        
    返回:
        增强后的提示
    """
    try:
        sanitized_prompt = request.prompt.replace("\r\n", "").replace("\n", "")  # 清理提示，移除换行符
        logger.info(f"Enhancing prompt: {sanitized_prompt}")  # 记录增强提示的内容

        # Convert string report_style to ReportStyle enum
        # 将字符串报告风格转换为ReportStyle枚举
        report_style = None
        if request.report_style:
            try:
                # Handle both uppercase and lowercase input
                # 处理大小写输入
                style_mapping = {
                    "ACADEMIC": ReportStyle.ACADEMIC,  # 学术风格
                    "POPULAR_SCIENCE": ReportStyle.POPULAR_SCIENCE,  # 科普风格
                    "NEWS": ReportStyle.NEWS,  # 新闻风格
                    "SOCIAL_MEDIA": ReportStyle.SOCIAL_MEDIA,  # 社交媒体风格
                    "academic": ReportStyle.ACADEMIC,
                    "popular_science": ReportStyle.POPULAR_SCIENCE,
                    "news": ReportStyle.NEWS,
                    "social_media": ReportStyle.SOCIAL_MEDIA,
                }
                report_style = style_mapping.get(
                    request.report_style, ReportStyle.ACADEMIC  # 默认为学术风格
                )
            except Exception:
                # If invalid style, default to ACADEMIC
                # 如果风格无效，默认为学术风格
                report_style = ReportStyle.ACADEMIC
        else:
            report_style = ReportStyle.ACADEMIC  # 默认为学术风格

        workflow = build_prompt_enhancer_graph()  # 构建提示增强器图
        final_state = workflow.invoke(
            {
                "prompt": request.prompt,  # 提示
                "context": request.context,  # 上下文
                "report_style": report_style,  # 报告风格
            }
        )  # 调用工作流
        return {"result": final_state["output"]}  # 返回增强后的提示
    except Exception as e:
        logger.exception(f"Error occurred during prompt enhancement: {str(e)}")  # 记录提示增强错误
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)  # 抛出内部服务器错误


@app.post("/api/mcp/server/metadata", response_model=MCPServerMetadataResponse)
async def mcp_server_metadata(request: MCPServerMetadataRequest):
    """
    MCP服务器元数据API端点
    
    参数:
        request: MCP服务器元数据请求对象
        
    返回:
        MCP服务器元数据响应
    """
    try:
        # Load the MCP tools
        # 加载MCP工具
        tools = load_mcp_tools()

        # Construct the response
        # 构建响应
        response = MCPServerMetadataResponse(
            schema_version="v1",
            server_info={
                "name": "DeerFlow",
                "version": "0.1.0",
            },
            capabilities={
                "tools": tools,
            },
        )
        return response
    except Exception as e:
        logger.exception(f"Error in MCP server metadata endpoint: {str(e)}")  # 记录MCP服务器元数据端点错误
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)  # 抛出内部服务器错误


@app.get("/api/rag/config", response_model=RAGConfigResponse)
async def rag_config():
    """
    RAG配置API端点
    
    返回:
        RAG配置响应
    """
    return {"provider": SELECTED_RAG_PROVIDER}  # 返回选定的RAG提供者


@app.get("/api/rag/resources", response_model=RAGResourcesResponse)
async def rag_resources(request: Annotated[RAGResourceRequest, Query()]):
    """
    RAG资源API端点
    
    参数:
        request: RAG资源请求对象
        
    返回:
        RAG资源响应
    """
    try:
        retriever = build_retriever(request.provider)  # 构建检索器
        return {"resources": retriever.get_resources()}  # 返回资源列表
    except Exception as e:
        logger.exception(f"Error in RAG resources endpoint: {str(e)}")  # 记录RAG资源端点错误
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR_DETAIL)  # 抛出内部服务器错误
