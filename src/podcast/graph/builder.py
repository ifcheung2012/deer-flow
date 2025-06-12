# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import END, START, StateGraph

from src.podcast.graph.audio_mixer_node import audio_mixer_node
from src.podcast.graph.script_writer_node import script_writer_node
from src.podcast.graph.state import PodcastState
from src.podcast.graph.tts_node import tts_node


def build_graph():
    """
    构建并返回播客工作流图
    
    返回:
        编译后的播客工作流图
    """
    # build state graph
    # 构建状态图
    builder = StateGraph(PodcastState)  # 创建状态图构建器，使用PodcastState作为状态类型
    builder.add_node("script_writer", script_writer_node)  # 添加脚本编写节点
    builder.add_node("tts", tts_node)  # 添加文本转语音节点
    builder.add_node("audio_mixer", audio_mixer_node)  # 添加音频混合节点
    builder.add_edge(START, "script_writer")  # 从开始节点连接到脚本编写节点
    builder.add_edge("script_writer", "tts")  # 从脚本编写节点连接到文本转语音节点
    builder.add_edge("tts", "audio_mixer")  # 从文本转语音节点连接到音频混合节点
    builder.add_edge("audio_mixer", END)  # 从音频混合节点连接到结束节点
    return builder.compile()  # 编译并返回工作流图


workflow = build_graph()  # 构建工作流图

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()  # 加载环境变量

    report_content = open("examples/nanjing_tangbao.md").read()  # 读取报告内容
    final_state = workflow.invoke({"input": report_content})  # 调用工作流
    for line in final_state["script"].lines:
        # 打印脚本行，<M>表示男性说话者，<F>表示女性说话者
        print("<M>" if line.speaker == "male" else "<F>", line.text)

    with open("final.mp3", "wb") as f:
        f.write(final_state["output"])  # 将输出写入MP3文件
