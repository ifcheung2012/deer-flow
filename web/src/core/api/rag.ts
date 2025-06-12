// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入资源类型
import type { Resource } from "../messages";

// 导入服务URL解析函数
import { resolveServiceURL } from "./resolve-service-url";

/**
 * 查询RAG资源
 * 根据查询字符串获取检索增强生成(RAG)相关的资源
 * RAG是一种结合检索和生成的AI技术，用于提供更准确的信息
 * 
 * @param {string} query - 查询字符串
 * @returns {Promise<Array<Resource>>} 资源数组
 */
export function queryRAGResources(query: string) {
  // 发送GET请求到RAG资源端点
  return fetch(resolveServiceURL(`rag/resources?query=${query}`), {
    method: "GET",
  })
    .then((res) => res.json()) // 解析JSON响应
    .then((res) => {
      return res.resources as Array<Resource>; // 返回资源数组
    })
    .catch((err) => {
      return []; // 出错时返回空数组
    });
}

/**
 * 获取RAG配置
 * 获取检索增强生成(RAG)系统的配置信息
 * 
 * @returns {Promise<any>} RAG提供者配置
 */
export function getRAGConfig() {
  // 发送GET请求到RAG配置端点
  return fetch(resolveServiceURL(`rag/config`), {
    method: "GET",
  })
    .then((res) => res.json()) // 解析JSON响应
    .then((res) => res.provider); // 返回提供者信息
}
