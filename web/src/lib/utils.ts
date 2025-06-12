// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入clsx库用于条件性地构建className字符串
import { clsx, type ClassValue } from "clsx"
// 导入tailwind-merge用于合并tailwind类名并解决冲突
import { twMerge } from "tailwind-merge"

/**
 * 组合并合并CSS类名
 * 使用clsx处理条件类名，然后用tailwind-merge解决Tailwind CSS类名冲突
 * 
 * @param {ClassValue[]} inputs - 要合并的类名数组
 * @returns {string} 合并后的类名字符串
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
