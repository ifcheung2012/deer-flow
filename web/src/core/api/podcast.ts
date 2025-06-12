// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入服务URL解析函数
import { resolveServiceURL } from "./resolve-service-url";

/**
 * 生成播客音频
 * 将文本内容转换为播客风格的音频
 * 
 * @param {string} content - 要转换为音频的文本内容
 * @returns {Promise<string>} 音频文件的URL
 * @throws {Error} 当HTTP请求失败时抛出错误
 */
export async function generatePodcast(content: string) {
  // 发送POST请求到播客生成端点
  const response = await fetch(resolveServiceURL("podcast/generate"), {
    method: "post",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content }), // 将内容序列化为JSON
  });
  
  // 检查响应状态
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  // 将响应转换为ArrayBuffer
  const arrayBuffer = await response.arrayBuffer();
  
  // 创建音频Blob对象
  const blob = new Blob([arrayBuffer], { type: "audio/mp3" });
  
  // 创建并返回Blob URL
  const audioUrl = URL.createObjectURL(blob);
  return audioUrl;
}
