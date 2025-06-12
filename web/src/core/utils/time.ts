// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 延迟执行函数
 * 创建一个Promise，在指定的毫秒数后解析
 * 可用于异步函数中的等待操作
 * 
 * @param {number} ms - 要等待的毫秒数
 * @returns {Promise<void>} 在指定时间后解析的Promise
 * @example
 * // 等待1秒
 * await sleep(1000);
 */
export function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
