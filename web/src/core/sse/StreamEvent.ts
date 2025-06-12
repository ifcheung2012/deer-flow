// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 流事件接口
 * 定义服务器发送事件(SSE)的基本结构
 * 用于在客户端和服务器之间进行实时数据传输
 */
export interface StreamEvent {
  event: string; // 事件类型
  data: string;  // 事件数据（通常是JSON字符串）
}
