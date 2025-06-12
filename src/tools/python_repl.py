# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import Annotated
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from .decorators import log_io

# Initialize REPL and logger
# 初始化REPL和日志记录器
repl = PythonREPL()
logger = logging.getLogger(__name__)


@tool
@log_io
def python_repl_tool(
    code: Annotated[
        str, "The python code to execute to do further analysis or calculation."
        # 要执行的Python代码，用于进一步分析或计算
    ],
):
    """Use this to execute python code and do data analysis or calculation. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    # 使用此工具执行Python代码并进行数据分析或计算。如果你想查看某个值的输出，
    # 应该使用`print(...)`将其打印出来。这对用户是可见的。
    
    if not isinstance(code, str):
        error_msg = f"Invalid input: code must be a string, got {type(code)}"
        logger.error(error_msg)
        return f"Error executing code:\n```python\n{code}\n```\nError: {error_msg}"
        # 错误：代码必须是字符串

    logger.info("Executing Python code")  # 执行Python代码
    try:
        result = repl.run(code)
        # Check if the result is an error message by looking for typical error patterns
        # 通过查找典型的错误模式来检查结果是否为错误消息
        if isinstance(result, str) and ("Error" in result or "Exception" in result):
            logger.error(result)
            return f"Error executing code:\n```python\n{code}\n```\nError: {result}"
            # 执行代码时出错
        logger.info("Code execution successful")  # 代码执行成功
    except BaseException as e:
        error_msg = repr(e)
        logger.error(error_msg)
        return f"Error executing code:\n```python\n{code}\n```\nError: {error_msg}"
        # 执行代码时出错

    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    # 成功执行：[代码] 标准输出：[结果]
    return result_str
