// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入MCP服务器元数据类型
import type { SimpleMCPServerMetadata } from "../mcp";

// 导入服务URL解析函数
import { resolveServiceURL } from "./resolve-service-url";

/**
 * 查询MCP服务器元数据
 * 向后端API发送请求，获取MCP服务器的详细元数据信息
 * MCP (Model Control Protocol) 用于控制和管理模型服务
 * 
 * @param {SimpleMCPServerMetadata} config - MCP服务器简单配置信息
 * @returns {Promise<any>} 服务器元数据响应
 * @throws {Error} 当HTTP请求失败时抛出错误
 */
export async function queryMCPServerMetadata(config: SimpleMCPServerMetadata) {
  // 发送POST请求到MCP服务器元数据端点
  const response = await fetch(resolveServiceURL("mcp/server/metadata"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(config), // 将配置序列化为JSON
  });
  
  // 检查响应状态
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  // 解析并返回响应JSON
  return response.json();
}
