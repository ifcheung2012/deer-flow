# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import json
import json_repair

logger = logging.getLogger(__name__)  # 获取日志记录器


def repair_json_output(content: str) -> str:
    """
    Repair and normalize JSON output.

    Args:
        content (str): String content that may contain JSON

    Returns:
        str: Repaired JSON string, or original content if not JSON
    """
    # 修复和规范化JSON输出
    #
    # 参数:
    #     content (str): 可能包含JSON的字符串内容
    #
    # 返回:
    #     str: 修复后的JSON字符串，如果不是JSON则返回原始内容
    
    content = content.strip()  # 去除首尾空白
    if content.startswith(("{", "[")) or "```json" in content or "```ts" in content:
        # 如果内容以{或[开头，或包含```json或```ts标记
        try:
            # If content is wrapped in ```json code block, extract the JSON part
            # 如果内容被```json代码块包裹，提取JSON部分
            if content.startswith("```json"):
                content = content.removeprefix("```json")  # 移除```json前缀

            if content.startswith("```ts"):
                content = content.removeprefix("```ts")  # 移除```ts前缀

            if content.endswith("```"):
                content = content.removesuffix("```")  # 移除```后缀

            # Try to repair and parse JSON
            # 尝试修复和解析JSON
            repaired_content = json_repair.loads(content)  # 使用json_repair库加载并修复JSON
            return json.dumps(repaired_content, ensure_ascii=False)  # 转换为JSON字符串，确保非ASCII字符不被转义
        except Exception as e:
            logger.warning(f"JSON repair failed: {e}")  # JSON修复失败
    return content  # 返回内容
