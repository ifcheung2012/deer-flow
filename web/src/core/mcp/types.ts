// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * MCP (Model Control Protocol) 类型定义文件
 * 定义与模型控制协议相关的接口和类型
 */

/**
 * MCP工具元数据接口
 * 描述可用工具的基本信息
 */
export interface MCPToolMetadata {
  name: string;        // 工具名称
  description: string; // 工具描述
  inputSchema?: Record<string, unknown>; // 输入参数模式
}

/**
 * 通用MCP服务器元数据接口
 * 服务器配置的基础接口，使用泛型指定传输类型
 * 
 * @template T 传输类型字符串
 */
export interface GenericMCPServerMetadata<T extends string> {
  name: string;        // 服务器名称
  transport: T;        // 传输类型
  enabled: boolean;    // 是否启用
  env?: Record<string, string>; // 环境变量
  tools: MCPToolMetadata[]; // 可用工具列表
  createdAt: number;   // 创建时间戳
  updatedAt: number;   // 更新时间戳
}

/**
 * 标准输入输出MCP服务器元数据接口
 * 使用标准输入输出(stdio)进行通信的服务器配置
 */
export interface StdioMCPServerMetadata
  extends GenericMCPServerMetadata<"stdio"> {
  transport: "stdio"; // 传输类型为stdio
  command: string;    // 执行命令
  args?: string[];    // 命令参数
}

/**
 * 简化的标准输入输出MCP服务器元数据类型
 * 省略了一些运行时属性，用于初始配置
 */
export type SimpleStdioMCPServerMetadata = Omit<
  StdioMCPServerMetadata,
  "enabled" | "tools" | "createdAt" | "updatedAt"
>;

/**
 * 服务器发送事件MCP服务器元数据接口
 * 使用SSE(Server-Sent Events)进行通信的服务器配置
 */
export interface SSEMCPServerMetadata extends GenericMCPServerMetadata<"sse"> {
  transport: "sse"; // 传输类型为sse
  url: string;      // 服务器URL
}

/**
 * 简化的服务器发送事件MCP服务器元数据类型
 * 省略了一些运行时属性，用于初始配置
 */
export type SimpleSSEMCPServerMetadata = Omit<
  SSEMCPServerMetadata,
  "enabled" | "tools" | "createdAt" | "updatedAt"
>;

/**
 * MCP服务器元数据联合类型
 * 包含所有可能的MCP服务器类型
 */
export type MCPServerMetadata = StdioMCPServerMetadata | SSEMCPServerMetadata;

/**
 * 简化的MCP服务器元数据联合类型
 * 用于初始配置的简化版本
 */
export type SimpleMCPServerMetadata =
  | SimpleStdioMCPServerMetadata
  | SimpleSSEMCPServerMetadata;
