import { parse } from "best-effort-json-parser";

/**
 * 解析JSON字符串
 * 具有容错能力，可以处理Markdown代码块中的JSON
 * 如果解析失败，则返回提供的回退值
 * 
 * @template T 预期的解析结果类型
 * @param {string | null | undefined} json - 要解析的JSON字符串
 * @param {T} fallback - 解析失败时返回的回退值
 * @returns {T} 解析结果或回退值
 */
export function parseJSON<T>(json: string | null | undefined, fallback: T) {
  // 如果输入为空，直接返回回退值
  if (!json) {
    return fallback;
  }
  try {
    // 处理可能包含在Markdown代码块中的JSON
    const raw = json
      .trim()
      .replace(/^```json\s*/, "") // 移除开头的```json
      .replace(/^```\s*/, "") // 移除开头的```
      .replace(/\s*```$/, ""); // 移除结尾的```
    return parse(raw) as T;
  } catch {
    // 解析失败时返回回退值
    return fallback;
  }
}
