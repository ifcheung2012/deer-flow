// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入环境变量
import { env } from "~/env";

/**
 * 解析服务URL
 * 根据环境变量中的API基础URL和提供的路径，构建完整的服务URL
 * 
 * @param {string} path - API路径（相对路径）
 * @returns {string} 完整的服务URL字符串
 */
export function resolveServiceURL(path: string) {
  // 获取API基础URL，如果未设置则使用本地开发URL
  let BASE_URL = env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/";
  
  // 确保基础URL以斜杠结尾
  if (!BASE_URL.endsWith("/")) {
    BASE_URL += "/";
  }
  
  // 构建并返回完整URL
  return new URL(path, BASE_URL).toString();
}
