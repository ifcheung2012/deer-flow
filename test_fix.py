#!/usr/bin/env python3
"""
This script manually patches sys.modules to fix the LLM import issue
so that tests can run without requiring LLM configuration.
"""
# 此脚本手动修补sys.modules以修复LLM导入问题，
# 使测试可以在不需要LLM配置的情况下运行。

import sys
from unittest.mock import MagicMock

# Create mocks
# 创建模拟对象
mock_llm = MagicMock()
mock_llm.invoke.return_value = "Mock LLM response"  # 模拟LLM响应

# Create a mock module for llm.py
# 为llm.py创建一个模拟模块
mock_llm_module = MagicMock()
mock_llm_module.get_llm_by_type = lambda llm_type: mock_llm
mock_llm_module.basic_llm = mock_llm
mock_llm_module._create_llm_use_conf = lambda llm_type, conf: mock_llm

# Set the mock module
# 设置模拟模块
sys.modules["src.llms.llm"] = mock_llm_module

print("Successfully patched LLM module. You can now run your tests.")  # 成功修补LLM模块。现在可以运行测试了。
print("Example: uv run pytest tests/test_types.py -v")  # 示例：uv run pytest tests/test_types.py -v
