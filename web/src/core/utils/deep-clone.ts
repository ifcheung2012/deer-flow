// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 深度克隆函数
 * 通过JSON序列化和反序列化实现对象的深拷贝
 * 注意：此方法不能克隆函数、Symbol、undefined、循环引用等
 * 
 * @template T 要克隆的值的类型
 * @param {T} value - 要深度克隆的值
 * @returns {T} 克隆后的值
 */
export function deepClone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value));
}
