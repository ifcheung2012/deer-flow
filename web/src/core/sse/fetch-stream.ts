// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入流事件类型
import { type StreamEvent } from "./StreamEvent";

/**
 * 获取事件流
 * 使用fetch API获取服务器发送事件(SSE)流
 * 将HTTP响应解析为流事件序列
 * 
 * @param {string} url - 请求URL
 * @param {RequestInit} init - 请求配置
 * @returns {AsyncIterable<StreamEvent>} 流事件异步迭代器
 * @throws {Error} 当请求失败或响应体不可读时抛出错误
 */
export async function* fetchStream(
  url: string,
  init: RequestInit,
): AsyncIterable<StreamEvent> {
  // 发送HTTP请求
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-cache", // 禁用缓存
    },
    ...init, // 合并自定义配置
  });
  
  // 检查响应状态
  if (response.status !== 200) {
    throw new Error(`Failed to fetch from ${url}: ${response.status}`);
  }
  
  // 从响应体读取事件流，事件总是以'\n\n'结束
  const reader = response.body
    ?.pipeThrough(new TextDecoderStream()) // 将字节流转换为文本流
    .getReader(); // 获取流读取器
    
  // 检查读取器是否可用
  if (!reader) {
    throw new Error("Response body is not readable");
  }
  
  // 缓冲区，用于存储未完成的事件数据
  let buffer = "";
  
  // 持续读取流
  while (true) {
    // 从读取器获取下一块数据
    const { done, value } = await reader.read();
    
    // 如果流已结束，退出循环
    if (done) {
      break;
    }
    
    // 将新数据添加到缓冲区
    buffer += value;
    
    // 处理缓冲区中的所有完整事件
    while (true) {
      // 查找事件结束标记
      const index = buffer.indexOf("\n\n");
      if (index === -1) {
        break; // 没有完整事件，等待更多数据
      }
      
      // 提取完整事件
      const chunk = buffer.slice(0, index);
      // 更新缓冲区，移除已处理的事件
      buffer = buffer.slice(index + 2);
      
      // 解析事件
      const event = parseEvent(chunk);
      if (event) {
        // 产生事件
        yield event;
      }
    }
  }
}

/**
 * 解析事件文本
 * 将SSE格式的文本解析为流事件对象
 * 
 * @param {string} chunk - 事件文本块
 * @returns {StreamEvent | undefined} 解析后的流事件，或undefined（如果解析失败）
 */
function parseEvent(chunk: string) {
  // 默认事件类型
  let resultEvent = "message";
  // 事件数据
  let resultData: string | null = null;
  
  // 按行解析事件文本
  for (const line of chunk.split("\n")) {
    // 查找键值分隔符
    const pos = line.indexOf(": ");
    if (pos === -1) {
      continue; // 跳过无效行
    }
    
    // 提取键和值
    const key = line.slice(0, pos);
    const value = line.slice(pos + 2);
    
    // 根据键设置相应的结果字段
    if (key === "event") {
      resultEvent = value; // 设置事件类型
    } else if (key === "data") {
      resultData = value; // 设置事件数据
    }
  }
  
  // 如果是默认事件类型且没有数据，则返回undefined
  if (resultEvent === "message" && resultData === null) {
    return undefined;
  }
  
  // 返回解析后的事件对象
  return {
    event: resultEvent,
    data: resultData,
  } as StreamEvent;
}
