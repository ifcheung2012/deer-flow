# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Literal

from pydantic import BaseModel, Field


class ScriptLine(BaseModel):
    """
    脚本行类，表示播客脚本中的一行
    
    属性:
        speaker: 说话者性别，可以是"male"(男性)或"female"(女性)
        paragraph: 段落文本内容
    """
    speaker: Literal["male", "female"] = Field(default="male")  # 说话者性别，默认为男性
    paragraph: str = Field(default="")  # 段落文本内容，默认为空字符串


class Script(BaseModel):
    """
    脚本类，表示完整的播客脚本
    
    属性:
        locale: 语言区域，可以是"en"(英语)或"zh"(中文)
        lines: 脚本行列表
    """
    locale: Literal["en", "zh"] = Field(default="en")  # 语言区域，默认为英语
    lines: list[ScriptLine] = Field(default=[])  # 脚本行列表，默认为空列表
