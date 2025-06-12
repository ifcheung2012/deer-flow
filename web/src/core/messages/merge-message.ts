// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入API事件类型
import type {
  ChatEvent,
  InterruptEvent,
  MessageChunkEvent,
  ToolCallChunksEvent,
  ToolCallResultEvent,
  ToolCallsEvent,
} from "../api";
// 导入深拷贝工具
import { deepClone } from "../utils/deep-clone";

// 导入消息类型
import type { Message } from "./types";

/**
 * 合并消息函数
 * 将新的聊天事件合并到现有消息中，根据事件类型进行不同处理
 * 
 * @param {Message} message - 要更新的消息对象
 * @param {ChatEvent} event - 新的聊天事件
 * @returns {Message} 合并后的消息对象（深拷贝）
 */
export function mergeMessage(message: Message, event: ChatEvent) {
  // 根据事件类型选择不同的合并策略
  if (event.type === "message_chunk") {
    // 合并文本消息
    mergeTextMessage(message, event);
  } else if (event.type === "tool_calls" || event.type === "tool_call_chunks") {
    // 合并工具调用消息
    mergeToolCallMessage(message, event);
  } else if (event.type === "tool_call_result") {
    // 合并工具调用结果消息
    mergeToolCallResultMessage(message, event);
  } else if (event.type === "interrupt") {
    // 合并中断消息
    mergeInterruptMessage(message, event);
  }
  
  // 处理消息完成状态
  if (event.data.finish_reason) {
    // 设置完成原因
    message.finishReason = event.data.finish_reason;
    // 标记流式传输结束
    message.isStreaming = false;
    
    // 处理工具调用参数
    if (message.toolCalls) {
      message.toolCalls.forEach((toolCall) => {
        if (toolCall.argsChunks?.length) {
          // 将参数分块合并并解析为JSON对象
          toolCall.args = JSON.parse(toolCall.argsChunks.join(""));
          // 删除参数分块，不再需要
          delete toolCall.argsChunks;
        }
      });
    }
  }
  
  // 返回消息的深拷贝，避免引用问题
  return deepClone(message);
}

/**
 * 合并文本消息
 * 将文本块添加到消息内容中
 * 
 * @param {Message} message - 要更新的消息对象
 * @param {MessageChunkEvent} event - 文本块事件
 */
function mergeTextMessage(message: Message, event: MessageChunkEvent) {
  if (event.data.content) {
    // 添加到完整内容
    message.content += event.data.content;
    // 保存到内容分块数组
    message.contentChunks.push(event.data.content);
  }
}

/**
 * 合并工具调用消息
 * 处理工具调用和工具调用分块事件
 * 
 * @param {Message} message - 要更新的消息对象
 * @param {ToolCallsEvent | ToolCallChunksEvent} event - 工具调用事件
 */
function mergeToolCallMessage(
  message: Message,
  event: ToolCallsEvent | ToolCallChunksEvent,
) {
  // 处理完整工具调用事件
  if (event.type === "tool_calls" && event.data.tool_calls[0]?.name) {
    // 创建工具调用数组
    message.toolCalls = event.data.tool_calls.map((raw) => ({
      id: raw.id,
      name: raw.name,
      args: raw.args,
      result: undefined,
    }));
  }

  // 确保工具调用数组存在
  message.toolCalls ??= [];
  
  // 处理工具调用分块
  for (const chunk of event.data.tool_call_chunks) {
    if (chunk.id) {
      // 如果分块有ID，查找对应的工具调用
      const toolCall = message.toolCalls.find(
        (toolCall) => toolCall.id === chunk.id,
      );
      if (toolCall) {
        toolCall.argsChunks = [chunk.args];
      }
    } else {
      const streamingToolCall = message.toolCalls.find(
        (toolCall) => toolCall.argsChunks?.length,
      );
      if (streamingToolCall) {
        streamingToolCall.argsChunks!.push(chunk.args);
      }
    }
  }
}

function mergeToolCallResultMessage(
  message: Message,
  event: ToolCallResultEvent,
) {
  const toolCall = message.toolCalls?.find(
    (toolCall) => toolCall.id === event.data.tool_call_id,
  );
  if (toolCall) {
    toolCall.result = event.data.content;
  }
}

function mergeInterruptMessage(message: Message, event: InterruptEvent) {
  message.isStreaming = false;
  message.options = event.data.options;
}
