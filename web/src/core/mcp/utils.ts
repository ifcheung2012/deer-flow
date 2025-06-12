// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入设置存储
import { useSettingsStore } from "../store";

/**
 * 查找MCP工具
 * 根据工具名称在所有已配置的MCP服务器中查找对应的工具
 * 
 * @param {string} name - 要查找的工具名称
 * @returns {MCPToolMetadata | null} 找到的工具元数据，如果未找到则返回null
 */
export function findMCPTool(name: string) {
  // 从设置存储中获取所有MCP服务器
  const mcpServers = useSettingsStore.getState().mcp.servers;
  
  // 遍历所有服务器
  for (const server of mcpServers) {
    // 遍历服务器中的所有工具
    for (const tool of server.tools) {
      // 如果找到匹配的工具名称，则返回该工具
      if (tool.name === name) {
        return tool;
      }
    }
  }
  
  // 未找到匹配的工具，返回null
  return null;
}
