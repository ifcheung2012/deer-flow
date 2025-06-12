// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入Next.js导航钩子
import { useSearchParams } from "next/navigation";
// 导入React钩子
import { useMemo } from "react";

// 导入环境变量
import { env } from "~/env";

// 导入回放ID提取函数
import { extractReplayIdFromSearchParams } from "./get-replay-id";

/**
 * 使用回放钩子
 * 检测当前应用是否处于回放模式，并提供回放相关信息
 * 
 * 回放模式有两种触发方式：
 * 1. URL中包含replay参数
 * 2. 应用处于静态网站模式
 * 
 * @returns {Object} 包含回放状态和回放ID的对象
 * @returns {boolean} returns.isReplay - 是否处于回放模式
 * @returns {string|null} returns.replayId - 回放ID，如果不是通过ID触发则为null
 */
export function useReplay() {
  // 获取URL搜索参数
  const searchParams = useSearchParams();
  
  // 从搜索参数中提取回放ID，并缓存结果
  const replayId = useMemo(
    () => extractReplayIdFromSearchParams(searchParams.toString()),
    [searchParams],
  );
  
  // 返回回放状态和ID
  return {
    isReplay: replayId != null || env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY, // 判断是否处于回放模式
    replayId, // 回放ID
  };
}
