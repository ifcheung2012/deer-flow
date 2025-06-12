// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入选项类型
import type { Option } from "../messages";

/**
 * API类型定义文件
 * 定义与API交互相关的接口和类型
 */

// ============= 工具调用相关类型 =============

/**
 * 工具调用接口
 * 表示对特定工具的完整调用
 */
export interface ToolCall {
  type: "tool_call"; // 类型标识
  id: string; // 调用唯一标识符
  name: string; // 工具名称
  args: Record<string, unknown>; // 工具参数
}

/**
 * 工具调用分块接口
 * 表示工具调用的部分内容，用于流式传输
 */
export interface ToolCallChunk {
  type: "tool_call_chunk"; // 类型标识
  index: number; // 分块索引
  id: string; // 调用唯一标识符
  name: string; // 工具名称
  args: string; // 工具参数（字符串形式）
}

// ============= 事件相关类型 =============

/**
 * 通用事件接口
 * 所有事件类型的基础接口
 * 
 * @template T 事件类型
 * @template D 事件数据类型
 */
interface GenericEvent<T extends string, D extends object> {
  type: T; // 事件类型
  data: {
    id: string; // 事件ID
    thread_id: string; // 线程ID
    agent: "coordinator" | "planner" | "researcher" | "coder" | "reporter"; // 代理类型
    role: "user" | "assistant" | "tool"; // 角色类型
    finish_reason?: "stop" | "tool_calls" | "interrupt"; // 完成原因
  } & D; // 扩展数据
}

/**
 * 消息分块事件接口
 * 表示消息内容的一部分，用于流式传输
 */
export interface MessageChunkEvent
  extends GenericEvent<
    "message_chunk",
    {
      content?: string; // 消息内容
    }
  > {}

/**
 * 工具调用事件接口
 * 表示完整的工具调用
 */
export interface ToolCallsEvent
  extends GenericEvent<
    "tool_calls",
    {
      tool_calls: ToolCall[]; // 完整工具调用列表
      tool_call_chunks: ToolCallChunk[]; // 工具调用分块列表
    }
  > {}

/**
 * 工具调用分块事件接口
 * 表示工具调用的部分内容
 */
export interface ToolCallChunksEvent
  extends GenericEvent<
    "tool_call_chunks",
    {
      tool_call_chunks: ToolCallChunk[]; // 工具调用分块列表
    }
  > {}

/**
 * 工具调用结果事件接口
 * 表示工具调用的执行结果
 */
export interface ToolCallResultEvent
  extends GenericEvent<
    "tool_call_result",
    {
      tool_call_id: string; // 工具调用ID
      content?: string; // 结果内容
    }
  > {}

/**
 * 中断事件接口
 * 表示流式传输被中断
 */
export interface InterruptEvent
  extends GenericEvent<
    "interrupt",
    {
      options: Option[]; // 中断选项
    }
  > {}

/**
 * 聊天事件联合类型
 * 包含所有可能的聊天相关事件类型
 */
export type ChatEvent =
  | MessageChunkEvent
  | ToolCallsEvent
  | ToolCallChunksEvent
  | ToolCallResultEvent
  | InterruptEvent;
