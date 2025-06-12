// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 消息模块类型定义文件
 * 定义与消息相关的接口和类型
 */

/**
 * 消息角色类型
 * 定义消息可能的发送者角色
 */
export type MessageRole = "user" | "assistant" | "tool";

/**
 * 消息接口
 * 定义系统中的消息结构
 */
export interface Message {
  id: string;         // 消息唯一标识符
  threadId: string;   // 所属会话线程ID
  agent?:             // 可选的代理类型
    | "coordinator"   // 协调者
    | "planner"       // 规划者
    | "researcher"    // 研究者
    | "coder"         // 编码者
    | "reporter"      // 报告者
    | "podcast";      // 播客
  role: MessageRole;  // 消息角色
  isStreaming?: boolean; // 是否正在流式传输
  content: string;    // 消息内容
  contentChunks: string[]; // 消息内容分块
  toolCalls?: ToolCallRuntime[]; // 可选的工具调用
  options?: Option[]; // 可选的选项列表
  finishReason?: "stop" | "interrupt" | "tool_calls"; // 完成原因
  interruptFeedback?: string; // 中断反馈
  resources?: Array<Resource>; // 相关资源
}

/**
 * 选项接口
 * 定义用户可选择的选项
 */
export interface Option {
  text: string;  // 选项显示文本
  value: string; // 选项值
}

/**
 * 工具调用运行时接口
 * 定义工具调用的运行时状态
 */
export interface ToolCallRuntime {
  id: string;    // 调用唯一标识符
  name: string;  // 工具名称
  args: Record<string, unknown>; // 工具参数
  argsChunks?: string[]; // 参数分块
  result?: string; // 调用结果
}

/**
 * 资源接口
 * 定义与消息相关的外部资源
 */
export interface Resource {
  uri: string;   // 资源URI
  title: string; // 资源标题
}
