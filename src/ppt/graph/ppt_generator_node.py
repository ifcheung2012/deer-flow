# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os
import subprocess
import uuid

from src.ppt.graph.state import PPTState

logger = logging.getLogger(__name__)  # 获取日志记录器


def ppt_generator_node(state: PPTState):
    """
    PPT生成节点函数
    
    使用marp-cli工具将Markdown内容转换为PPT文件
    
    参数:
        state: PPT状态对象
        
    返回:
        包含生成的PPT文件路径的字典
    """
    logger.info("Generating ppt file...")  # 记录正在生成PPT文件的信息
    # use marp cli to generate ppt file
    # 使用marp-cli工具生成PPT文件
    # https://github.com/marp-team/marp-cli?tab=readme-ov-file
    generated_file_path = os.path.join(
        os.getcwd(), f"generated_ppt_{uuid.uuid4()}.pptx"  # 创建生成的PPT文件路径
    )
    subprocess.run(["marp", state["ppt_file_path"], "-o", generated_file_path])  # 调用marp命令行工具生成PPT
    # remove the temp file
    # 删除临时文件
    os.remove(state["ppt_file_path"])  # 删除临时Markdown文件
    logger.info(f"generated_file_path: {generated_file_path}")  # 记录生成的PPT文件路径
    return {"generated_file_path": generated_file_path}  # 返回包含生成的PPT文件路径的字典
