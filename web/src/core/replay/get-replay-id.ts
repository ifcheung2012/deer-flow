// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 从URL搜索参数中提取回放ID
 * 用于获取当前请求中的回放标识符
 * 
 * @param {string} params - URL搜索参数字符串
 * @returns {string | null} 回放ID，如果不存在则返回null
 */
export function extractReplayIdFromSearchParams(params: string) {
  // 解析URL搜索参数
  const urlParams = new URLSearchParams(params);
  
  // 检查是否存在replay参数
  if (urlParams.has("replay")) {
    // 返回replay参数值
    return urlParams.get("replay");
  }
  
  // 不存在replay参数，返回null
  return null;
}
