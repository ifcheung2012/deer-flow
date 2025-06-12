# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import functools
from typing import Any, Callable, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")  # 类型变量T


def log_io(func: Callable) -> Callable:
    """
    A decorator that logs the input parameters and output of a tool function.

    Args:
        func: The tool function to be decorated

    Returns:
        The wrapped function with input/output logging
    """
    # 一个装饰器，用于记录工具函数的输入参数和输出
    #
    # 参数:
    #     func: 要装饰的工具函数
    #
    # 返回:
    #     带有输入/输出日志记录的包装函数

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Log input parameters
        # 记录输入参数
        func_name = func.__name__
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.info(f"Tool {func_name} called with parameters: {params}")

        # Execute the function
        # 执行函数
        result = func(*args, **kwargs)

        # Log the output
        # 记录输出
        logger.info(f"Tool {func_name} returned: {result}")

        return result

    return wrapper


class LoggedToolMixin:
    """A mixin class that adds logging functionality to any tool."""
    # 一个混入类，为任何工具添加日志功能

    def _log_operation(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Helper method to log tool operations."""
        # 记录工具操作的辅助方法
        tool_name = self.__class__.__name__.replace("Logged", "")
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.debug(f"Tool {tool_name}.{method_name} called with parameters: {params}")

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Override _run method to add logging."""
        # 重写_run方法以添加日志记录
        self._log_operation("_run", *args, **kwargs)
        result = super()._run(*args, **kwargs)
        logger.debug(
            f"Tool {self.__class__.__name__.replace('Logged', '')} returned: {result}"
        )
        return result


def create_logged_tool(base_tool_class: Type[T]) -> Type[T]:
    """
    Factory function to create a logged version of any tool class.

    Args:
        base_tool_class: The original tool class to be enhanced with logging

    Returns:
        A new class that inherits from both LoggedToolMixin and the base tool class
    """
    # 工厂函数，用于创建任何工具类的日志版本
    #
    # 参数:
    #     base_tool_class: 要增强日志功能的原始工具类
    #
    # 返回:
    #     一个同时继承LoggedToolMixin和基础工具类的新类

    class LoggedTool(LoggedToolMixin, base_tool_class):
        pass

    # Set a more descriptive name for the class
    # 为类设置更具描述性的名称
    LoggedTool.__name__ = f"Logged{base_tool_class.__name__}"
    return LoggedTool
