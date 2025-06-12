// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入服务URL解析函数
import { resolveServiceURL } from "./resolve-service-url";

/**
 * 增强提示请求接口
 * 定义发送到提示增强API的请求参数
 */
export interface EnhancePromptRequest {
  prompt: string;      // 原始提示文本
  context?: string;    // 可选的上下文信息
  report_style?: string; // 可选的报告风格
}

/**
 * 增强提示响应接口
 * 定义从提示增强API返回的响应结构
 */
export interface EnhancePromptResponse {
  enhanced_prompt: string; // 增强后的提示文本
}

/**
 * 增强提示函数
 * 通过API将原始提示转换为更有效的增强提示
 * 
 * @param {EnhancePromptRequest} request - 增强提示请求对象
 * @returns {Promise<string>} 增强后的提示文本
 * @throws {Error} 当HTTP请求失败时抛出错误
 */
export async function enhancePrompt(
  request: EnhancePromptRequest,
): Promise<string> {
  // 发送POST请求到提示增强端点
  const response = await fetch(resolveServiceURL("prompt/enhance"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request), // 将请求序列化为JSON
  });

  // 检查响应状态
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // 解析响应数据
  const data = await response.json();
  console.log("Raw API response:", data); // 调试日志

  // 后端现在直接在result字段中返回增强的提示
  let enhancedPrompt = data.result;

  // 如果结果仍然是JSON对象，提取enhanced_prompt字段
  if (typeof enhancedPrompt === "object" && enhancedPrompt.enhanced_prompt) {
    enhancedPrompt = enhancedPrompt.enhanced_prompt;
  }

  // 如果结果是JSON字符串，尝试解析它
  if (typeof enhancedPrompt === "string") {
    try {
      const parsed = JSON.parse(enhancedPrompt);
      if (parsed.enhanced_prompt) {
        enhancedPrompt = parsed.enhanced_prompt;
      }
    } catch {
      // 如果解析失败，直接使用字符串（这是我们想要的）
      console.log("Using enhanced prompt as-is:", enhancedPrompt);
    }
  }

  // 如果出现问题，回退到原始提示
  if (!enhancedPrompt || enhancedPrompt.trim() === "") {
    console.warn("No enhanced prompt received, using original");
    enhancedPrompt = request.prompt;
  }

  return enhancedPrompt;
}
