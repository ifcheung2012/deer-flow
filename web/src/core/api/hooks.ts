// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入React钩子
import { useEffect, useRef, useState } from "react";

// 导入环境变量
import { env } from "~/env";

// 导入回放相关功能
import { useReplay } from "../replay";

// 导入API函数
import { fetchReplayTitle } from "./chat";
import { getRAGConfig } from "./rag";

/**
 * 使用回放元数据钩子
 * 获取回放会话的元数据，如标题
 * 
 * @returns {Object} 包含标题、加载状态和错误状态的对象
 */
export function useReplayMetadata() {
  // 获取是否处于回放模式
  const { isReplay } = useReplay();
  // 标题状态
  const [title, setTitle] = useState<string | null>(null);
  // 加载状态引用，避免重复请求
  const isLoading = useRef(false);
  // 错误状态
  const [error, setError] = useState<boolean>(false);
  
  // 当组件挂载或回放状态变化时获取标题
  useEffect(() => {
    // 非回放模式不需要获取标题
    if (!isReplay) {
      return;
    }
    // 已有标题或正在加载中则不重复请求
    if (title || isLoading.current) {
      return;
    }
    
    // 设置加载状态并请求标题
    isLoading.current = true;
    fetchReplayTitle()
      .then((title) => {
        // 成功获取标题
        setError(false);
        setTitle(title ?? null);
        // 更新页面标题
        if (title) {
          document.title = `${title} - DeerFlow`;
        }
      })
      .catch(() => {
        // 获取标题失败
        setError(true);
        setTitle("Error: the replay is not available.");
        document.title = "DeerFlow";
      })
      .finally(() => {
        // 重置加载状态
        isLoading.current = false;
      });
  }, [isLoading, isReplay, title]);
  
  return { title, isLoading, hasError: error };
}

/**
 * 使用RAG提供者钩子
 * 获取检索增强生成(RAG)系统的提供者信息
 * 
 * @returns {Object} 包含提供者和加载状态的对象
 */
export function useRAGProvider() {
  // 加载状态
  const [loading, setLoading] = useState(true);
  // 提供者状态
  const [provider, setProvider] = useState<string | null>(null);

  // 组件挂载时获取RAG配置
  useEffect(() => {
    // 静态网站模式不需要获取RAG配置
    if (env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY) {
      setLoading(false);
      return;
    }
    
    // 请求RAG配置
    getRAGConfig()
      .then(setProvider) // 设置提供者
      .catch((e) => {
        // 获取配置失败
        setProvider(null);
        console.error("Failed to get RAG provider", e);
      })
      .finally(() => {
        // 重置加载状态
        setLoading(false);
      });
  }, []);

  return { provider, loading };
}
