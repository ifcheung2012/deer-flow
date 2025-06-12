// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { nanoid } from "nanoid";
import { toast } from "sonner";
import { create } from "zustand";
import { useShallow } from "zustand/react/shallow";

import { chatStream, generatePodcast } from "../api";
import type { Message, Resource } from "../messages";
import { mergeMessage } from "../messages";
import { parseJSON } from "../utils";

import { getChatStreamSettings } from "./settings-store";

const THREAD_ID = nanoid();

/**
 * 主存储钩子
 * 使用Zustand管理应用全局状态
 * 包括消息、研究、响应状态等
 */
export const useStore = create<{
  responding: boolean;
  threadId: string | undefined;
  messageIds: string[];
  messages: Map<string, Message>;
  researchIds: string[];
  researchPlanIds: Map<string, string>;
  researchReportIds: Map<string, string>;
  researchActivityIds: Map<string, string[]>;
  ongoingResearchId: string | null;
  openResearchId: string | null;

  appendMessage: (message: Message) => void;
  updateMessage: (message: Message) => void;
  updateMessages: (messages: Message[]) => void;
  openResearch: (researchId: string | null) => void;
  closeResearch: () => void;
  setOngoingResearch: (researchId: string | null) => void;
}>((set) => ({
  responding: false,
  threadId: THREAD_ID,
  messageIds: [],
  messages: new Map<string, Message>(),
  researchIds: [],
  researchPlanIds: new Map<string, string>(),
  researchReportIds: new Map<string, string>(),
  researchActivityIds: new Map<string, string[]>(),
  ongoingResearchId: null,
  openResearchId: null,

  appendMessage(message: Message) {
    set((state) => ({
      messageIds: [...state.messageIds, message.id],
      messages: new Map(state.messages).set(message.id, message),
    }));
  },
  updateMessage(message: Message) {
    set((state) => ({
      messages: new Map(state.messages).set(message.id, message),
    }));
  },
  updateMessages(messages: Message[]) {
    set((state) => {
      const newMessages = new Map(state.messages);
      messages.forEach((m) => newMessages.set(m.id, m));
      return { messages: newMessages };
    });
  },
  openResearch(researchId: string | null) {
    set({ openResearchId: researchId });
  },
  closeResearch() {
    set({ openResearchId: null });
  },
  setOngoingResearch(researchId: string | null) {
    set({ ongoingResearchId: researchId });
  },
}));

/**
 * 发送消息函数
 * 向AI发送用户消息并处理响应流
 * 
 * @param {string} [content] - 消息内容
 * @param {Object} [options] - 附加选项
 * @param {string} [options.interruptFeedback] - 中断反馈
 * @param {Array<Resource>} [options.resources] - 附加资源
 * @param {Object} [abortOptions] - 中止选项
 * @param {AbortSignal} [abortOptions.abortSignal] - 中止信号
 */
export async function sendMessage(
  content?: string,
  {
    interruptFeedback,
    resources,
  }: {
    interruptFeedback?: string;
    resources?: Array<Resource>;
  } = {},
  options: { abortSignal?: AbortSignal } = {},
) {
  if (content != null) {
    appendMessage({
      id: nanoid(),
      threadId: THREAD_ID,
      role: "user",
      content: content,
      contentChunks: [content],
      resources,
    });
  }

  const settings = getChatStreamSettings();
  const stream = chatStream(
    content ?? "[REPLAY]",
    {
      thread_id: THREAD_ID,
      interrupt_feedback: interruptFeedback,
      resources,
      auto_accepted_plan: settings.autoAcceptedPlan,
      enable_background_investigation:
        settings.enableBackgroundInvestigation ?? true,
      max_plan_iterations: settings.maxPlanIterations,
      max_step_num: settings.maxStepNum,
      max_search_results: settings.maxSearchResults,
      report_style: settings.reportStyle,
      mcp_settings: settings.mcpSettings,
    },
    options,
  );

  setResponding(true);
  let messageId: string | undefined;
  try {
    for await (const event of stream) {
      const { type, data } = event;
      messageId = data.id;
      let message: Message | undefined;
      if (type === "tool_call_result") {
        message = findMessageByToolCallId(data.tool_call_id);
      } else if (!existsMessage(messageId)) {
        message = {
          id: messageId,
          threadId: data.thread_id,
          agent: data.agent,
          role: data.role,
          content: "",
          contentChunks: [],
          isStreaming: true,
          interruptFeedback,
        };
        appendMessage(message);
      }
      message ??= getMessage(messageId);
      if (message) {
        message = mergeMessage(message, event);
        updateMessage(message);
      }
    }
  } catch {
    toast("An error occurred while generating the response. Please try again.");
    // Update message status.
    // TODO: const isAborted = (error as Error).name === "AbortError";
    if (messageId != null) {
      const message = getMessage(messageId);
      if (message?.isStreaming) {
        message.isStreaming = false;
        useStore.getState().updateMessage(message);
      }
    }
    useStore.getState().setOngoingResearch(null);
  } finally {
    setResponding(false);
  }
}

/**
 * 设置响应状态
 * @param {boolean} value - 是否正在响应
 */
function setResponding(value: boolean) {
  useStore.setState({ responding: value });
}

/**
 * 检查消息是否存在
 * @param {string} id - 消息ID
 * @returns {boolean} 是否存在
 */
function existsMessage(id: string) {
  return useStore.getState().messageIds.includes(id);
}

/**
 * 获取消息
 * @param {string} id - 消息ID
 * @returns {Message|undefined} 消息对象
 */
function getMessage(id: string) {
  return useStore.getState().messages.get(id);
}

/**
 * 根据工具调用ID查找消息
 * @param {string} toolCallId - 工具调用ID
 * @returns {Message|undefined} 包含该工具调用的消息
 */
function findMessageByToolCallId(toolCallId: string) {
  return Array.from(useStore.getState().messages.values())
    .reverse()
    .find((message) => {
      if (message.toolCalls) {
        return message.toolCalls.some((toolCall) => toolCall.id === toolCallId);
      }
      return false;
    });
}

/**
 * 添加消息到存储
 * 并处理研究相关逻辑
 * @param {Message} message - 要添加的消息
 */
function appendMessage(message: Message) {
  // 如果是研究相关的代理发送的消息
  if (
    message.agent === "coder" ||
    message.agent === "reporter" ||
    message.agent === "researcher"
  ) {
    // 如果没有正在进行的研究，创建新研究
    if (!getOngoingResearchId()) {
      const id = message.id;
      appendResearch(id);
      openResearch(id);
    }
    // 添加到研究活动
    appendResearchActivity(message);
  }
  // 添加消息到存储
  useStore.getState().appendMessage(message);
}

/**
 * 更新消息
 * 处理研究状态更新逻辑
 * @param {Message} message - 要更新的消息
 */
function updateMessage(message: Message) {
  // 如果有正在进行的研究，且消息来自reporter且已完成流式传输，则结束研究
  if (
    getOngoingResearchId() &&
    message.agent === "reporter" &&
    !message.isStreaming
  ) {
    useStore.getState().setOngoingResearch(null);
  }
  // 更新消息
  useStore.getState().updateMessage(message);
}

/**
 * 获取正在进行的研究ID
 * @returns {string|null} 研究ID或null
 */
function getOngoingResearchId() {
  return useStore.getState().ongoingResearchId;
}

/**
 * 添加新研究
 * 关联计划消息和研究ID
 * @param {string} researchId - 研究ID
 */
function appendResearch(researchId: string) {
  // 查找最近的计划消息
  let planMessage: Message | undefined;
  const reversedMessageIds = [...useStore.getState().messageIds].reverse();
  for (const messageId of reversedMessageIds) {
    const message = getMessage(messageId);
    if (message?.agent === "planner") {
      planMessage = message;
      break;
    }
  }
  
  // 创建消息ID列表，包含计划消息和研究消息
  const messageIds = [researchId];
  messageIds.unshift(planMessage!.id);
  
  // 更新状态
  useStore.setState({
    ongoingResearchId: researchId,
    researchIds: [...useStore.getState().researchIds, researchId],
    researchPlanIds: new Map(useStore.getState().researchPlanIds).set(
      researchId,
      planMessage!.id,
    ),
    researchActivityIds: new Map(useStore.getState().researchActivityIds).set(
      researchId,
      messageIds,
    ),
  });
}

/**
 * 添加消息到研究活动
 * 跟踪研究相关的消息
 * @param {Message} message - 要添加的消息
 */
function appendResearchActivity(message: Message) {
  const researchId = getOngoingResearchId();
  if (researchId) {
    // 获取当前研究活动消息列表
    const researchActivityIds = useStore.getState().researchActivityIds;
    const current = researchActivityIds.get(researchId)!;
    
    // 如果消息不在列表中，则添加
    if (!current.includes(message.id)) {
      useStore.setState({
        researchActivityIds: new Map(researchActivityIds).set(researchId, [
          ...current,
          message.id,
        ]),
      });
    }
    
    // 如果是报告消息，更新研究报告ID映射
    if (message.agent === "reporter") {
      useStore.setState({
        researchReportIds: new Map(useStore.getState().researchReportIds).set(
          researchId,
          message.id,
        ),
      });
    }
  }
}

/**
 * 打开研究面板
 * @param {string|null} researchId - 要打开的研究ID
 */
export function openResearch(researchId: string | null) {
  useStore.getState().openResearch(researchId);
}

/**
 * 关闭研究面板
 */
export function closeResearch() {
  useStore.getState().closeResearch();
}

/**
 * 生成并播放研究播客
 * 基于研究报告生成音频内容
 * @param {string} researchId - 研究ID
 */
export async function listenToPodcast(researchId: string) {
  // 获取计划和报告消息ID
  const planMessageId = useStore.getState().researchPlanIds.get(researchId);
  const reportMessageId = useStore.getState().researchReportIds.get(researchId);
  
  if (planMessageId && reportMessageId) {
    // 获取计划消息和标题
    const planMessage = getMessage(planMessageId)!;
    const title = parseJSON(planMessage.content, { title: "Untitled" }).title;
    
    // 获取报告消息
    const reportMessage = getMessage(reportMessageId);
    if (reportMessage?.content) {
      // 添加用户请求消息
      appendMessage({
        id: nanoid(),
        threadId: THREAD_ID,
        role: "user",
        content: "Please generate a podcast for the above research.",
        contentChunks: [],
      });
      
      // 创建播客消息
      const podCastMessageId = nanoid();
      const podcastObject = { title, researchId };
      const podcastMessage: Message = {
        id: podCastMessageId,
        threadId: THREAD_ID,
        role: "assistant",
        agent: "podcast",
        content: JSON.stringify(podcastObject),
        contentChunks: [],
        isStreaming: true,
      };
      appendMessage(podcastMessage);
      
      // 生成播客音频
      let audioUrl: string | undefined;
      try {
        audioUrl = await generatePodcast(reportMessage.content);
      } catch (e) {
        // 处理错误
        console.error(e);
        useStore.setState((state) => ({
          messages: new Map(useStore.getState().messages).set(
            podCastMessageId,
            {
              ...state.messages.get(podCastMessageId)!,
              content: JSON.stringify({
                ...podcastObject,
                error: e instanceof Error ? e.message : "Unknown error",
              }),
              isStreaming: false,
            },
          ),
        }));
        toast("An error occurred while generating podcast. Please try again.");
        return;
      }
      
      // 更新播客消息，添加音频URL
      useStore.setState((state) => ({
        messages: new Map(useStore.getState().messages).set(podCastMessageId, {
          ...state.messages.get(podCastMessageId)!,
          content: JSON.stringify({ ...podcastObject, audioUrl }),
          isStreaming: false,
        }),
      }));
    }
  }
}

/**
 * 获取研究相关消息的钩子
 * @param {string} researchId - 研究ID
 * @returns {Message|undefined} 研究计划消息
 */
export function useResearchMessage(researchId: string) {
  return useStore(
    useShallow((state) => {
      const messageId = state.researchPlanIds.get(researchId);
      return messageId ? state.messages.get(messageId) : undefined;
    }),
  );
}

/**
 * 获取单条消息的钩子
 * @param {string|null|undefined} messageId - 消息ID
 * @returns {Message|undefined} 消息对象
 */
export function useMessage(messageId: string | null | undefined) {
  return useStore(
    useShallow((state) =>
      messageId ? state.messages.get(messageId) : undefined,
    ),
  );
}

/**
 * 获取所有消息ID的钩子
 * @returns {string[]} 消息ID数组
 */
export function useMessageIds() {
  return useStore(useShallow((state) => state.messageIds));
}

/**
 * 获取最后一条中断消息的钩子
 * @returns {Message|undefined} 中断消息
 */
export function useLastInterruptMessage() {
  return useStore(
    useShallow((state) => {
      if (state.messageIds.length >= 2) {
        const lastMessage = state.messages.get(
          state.messageIds[state.messageIds.length - 1]!,
        );
        return lastMessage?.finishReason === "interrupt" ? lastMessage : null;
      }
      return null;
    }),
  );
}

export function useLastFeedbackMessageId() {
  const waitingForFeedbackMessageId = useStore(
    useShallow((state) => {
      if (state.messageIds.length >= 2) {
        const lastMessage = state.messages.get(
          state.messageIds[state.messageIds.length - 1]!,
        );
        if (lastMessage && lastMessage.finishReason === "interrupt") {
          return state.messageIds[state.messageIds.length - 2];
        }
      }
      return null;
    }),
  );
  return waitingForFeedbackMessageId;
}

export function useToolCalls() {
  return useStore(
    useShallow((state) => {
      return state.messageIds
        ?.map((id) => getMessage(id)?.toolCalls)
        .filter((toolCalls) => toolCalls != null)
        .flat();
    }),
  );
}
