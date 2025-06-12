// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入环境变量
import { env } from "~/env";

// 导入类型和工具函数
import type { MCPServerMetadata } from "../mcp";
import type { Resource } from "../messages";
import { extractReplayIdFromSearchParams } from "../replay/get-replay-id";
import { fetchStream } from "../sse";
import { sleep } from "../utils";

// 导入API相关函数和类型
import { resolveServiceURL } from "./resolve-service-url";
import type { ChatEvent } from "./types";

/**
 * 聊天流函数
 * 创建与后端的流式通信，用于实时聊天交互
 * 
 * @param {string} userMessage - 用户消息内容
 * @param {Object} params - 聊天参数
 * @param {string} params.thread_id - 会话线程ID
 * @param {Array<Resource>} [params.resources] - 可选的资源列表
 * @param {boolean} params.auto_accepted_plan - 是否自动接受计划
 * @param {number} params.max_plan_iterations - 最大计划迭代次数
 * @param {number} params.max_step_num - 最大步骤数
 * @param {number} [params.max_search_results] - 最大搜索结果数
 * @param {string} [params.interrupt_feedback] - 中断反馈
 * @param {boolean} params.enable_background_investigation - 是否启用背景调查
 * @param {string} [params.report_style] - 报告风格
 * @param {Object} [params.mcp_settings] - MCP设置
 * @param {Object} [options] - 请求选项
 * @param {AbortSignal} [options.abortSignal] - 中止信号
 * @returns {AsyncGenerator<ChatEvent>} 聊天事件异步生成器
 */
export async function* chatStream(
  userMessage: string,
  params: {
    thread_id: string;
    resources?: Array<Resource>;
    auto_accepted_plan: boolean;
    max_plan_iterations: number;
    max_step_num: number;
    max_search_results?: number;
    interrupt_feedback?: string;
    enable_background_investigation: boolean;
    report_style?: "academic" | "popular_science" | "news" | "social_media";
    mcp_settings?: {
      servers: Record<
        string,
        MCPServerMetadata & {
          enabled_tools: string[];
          add_to_agents: string[];
        }
      >;
    };
  },
  options: { abortSignal?: AbortSignal } = {},
) {
  // 检查是否使用静态网站模式、模拟模式或回放模式
  if (
    env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY ||
    location.search.includes("mock") ||
    location.search.includes("replay=")
  ) {
    // 使用回放流
    return yield* chatReplayStream(userMessage, params, options);
  }
  
  // 创建实际的聊天流
  const stream = fetchStream(resolveServiceURL("chat/stream"), {
    body: JSON.stringify({
      messages: [{ role: "user", content: userMessage }],
      ...params,
    }),
    signal: options.abortSignal,
  });
  
  // 处理流中的每个事件
  for await (const event of stream) {
    yield {
      type: event.event,
      data: JSON.parse(event.data),
    } as ChatEvent;
  }
}

/**
 * 聊天回放流函数
 * 用于模拟或回放聊天交互，主要用于演示和测试
 * 
 * @param {string} userMessage - 用户消息内容
 * @param {Object} params - 聊天参数
 * @param {Object} [options] - 请求选项
 * @returns {AsyncIterable<ChatEvent>} 聊天事件异步迭代器
 */
async function* chatReplayStream(
  userMessage: string,
  params: {
    thread_id: string;
    auto_accepted_plan: boolean;
    max_plan_iterations: number;
    max_step_num: number;
    max_search_results?: number;
    interrupt_feedback?: string;
  } = {
    thread_id: "__mock__",
    auto_accepted_plan: false,
    max_plan_iterations: 3,
    max_step_num: 1,
    max_search_results: 3,
    interrupt_feedback: undefined,
  },
  options: { abortSignal?: AbortSignal } = {},
): AsyncIterable<ChatEvent> {
  // 解析URL参数
  const urlParams = new URLSearchParams(window.location.search);
  let replayFilePath = "";
  
  // 确定回放文件路径
  if (urlParams.has("mock")) {
    if (urlParams.get("mock")) {
      replayFilePath = `/mock/${urlParams.get("mock")!}.txt`;
    } else {
      if (params.interrupt_feedback === "accepted") {
        replayFilePath = "/mock/final-answer.txt";
      } else if (params.interrupt_feedback === "edit_plan") {
        replayFilePath = "/mock/re-plan.txt";
      } else {
        replayFilePath = "/mock/first-plan.txt";
      }
    }
    fastForwardReplaying = true;
  } else {
    // 从URL中提取回放ID
    const replayId = extractReplayIdFromSearchParams(window.location.search);
    if (replayId) {
      replayFilePath = `/replay/${replayId}.txt`;
    } else {
      // 回退到默认回放
      replayFilePath = `/replay/eiffel-tower-vs-tallest-building.txt`;
    }
  }
  
  // 获取回放文本内容
  const text = await fetchReplay(replayFilePath, {
    abortSignal: options.abortSignal,
  });
  
  // 规范化文本并分割成块
  const normalizedText = text.replace(/\r\n/g, "\n");
  const chunks = normalizedText.split("\n\n");
  
  // 处理每个块
  for (const chunk of chunks) {
    const [eventRaw, dataRaw] = chunk.split("\n") as [string, string];
    const [, event] = eventRaw.split("event: ", 2) as [string, string];
    const [, data] = dataRaw.split("data: ", 2) as [string, string];

    try {
      // 构造聊天事件
      const chatEvent = {
        type: event,
        data: JSON.parse(data),
      } as ChatEvent;
      
      // 根据事件类型添加延迟，模拟真实交互
      if (chatEvent.type === "message_chunk") {
        if (!chatEvent.data.finish_reason) {
          await sleepInReplay(50);
        }
      } else if (chatEvent.type === "tool_call_result") {
        await sleepInReplay(500);
      }
      
      // 产生事件
      yield chatEvent;
      
      // 事件后的延迟
      if (chatEvent.type === "tool_call_result") {
        await sleepInReplay(800);
      } else if (chatEvent.type === "message_chunk") {
        if (chatEvent.data.role === "user") {
          await sleepInReplay(500);
        }
      }
    } catch (e) {
      console.error(e);
    }
  }
}

/**
 * 回放缓存
 * 存储已获取的回放内容，避免重复请求
 */
const replayCache = new Map<string, string>();

/**
 * 获取回放内容
 * 从指定URL获取回放文本，并缓存结果
 * 
 * @param {string} url - 回放文件URL
 * @param {Object} [options] - 请求选项
 * @returns {Promise<string>} 回放文本内容
 * @throws {Error} 当获取失败时抛出错误
 */
export async function fetchReplay(
  url: string,
  options: { abortSignal?: AbortSignal } = {},
) {
  // 检查缓存
  if (replayCache.has(url)) {
    return replayCache.get(url)!;
  }
  
  // 发送请求
  const res = await fetch(url, {
    signal: options.abortSignal,
  });
  
  // 检查响应状态
  if (!res.ok) {
    throw new Error(`Failed to fetch replay: ${res.statusText}`);
  }
  
  // 获取文本并缓存
  const text = await res.text();
  replayCache.set(url, text);
  return text;
}

/**
 * 获取回放标题
 * 从回放中提取第一个消息内容作为标题
 * 
 * @returns {Promise<string|undefined>} 回放标题
 */
export async function fetchReplayTitle() {
  const res = chatReplayStream(
    "",
    {
      thread_id: "__mock__",
      auto_accepted_plan: false,
      max_plan_iterations: 3,
      max_step_num: 1,
      max_search_results: 3,
    },
    {},
  );
  
  // 查找第一个消息块作为标题
  for await (const event of res) {
    if (event.type === "message_chunk") {
      return event.data.content;
    }
  }
}

/**
 * 回放中的延迟函数
 * 根据是否快进模式决定延迟时间
 * 
 * @param {number} ms - 延迟毫秒数
 * @returns {Promise<void>} 延迟完成的Promise
 */
export async function sleepInReplay(ms: number) {
  if (fastForwardReplaying) {
    await sleep(0); // 快进模式，无延迟
  } else {
    await sleep(ms); // 正常模式，按指定时间延迟
  }
}

/**
 * 快进回放标志
 * 控制回放速度
 */
let fastForwardReplaying = false;

/**
 * 设置回放快进状态
 * 
 * @param {boolean} value - 是否启用快进
 */
export function fastForwardReplay(value: boolean) {
  fastForwardReplaying = value;
}
