// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入HAST（HTML抽象语法树）类型
import type { Element, Root, ElementContent } from "hast";
// 导入树遍历工具
import { visit } from "unist-util-visit";
import type { BuildVisitor } from "unist-util-visit";

/**
 * Rehype插件：将文本按词分割为span元素
 * 用于创建逐词淡入动画效果
 * 特别适用于中文文本的分词处理
 * 
 * @returns {function} Rehype插件转换函数
 */
export function rehypeSplitWordsIntoSpans() {
  // 返回转换函数
  return (tree: Root) => {
    // 访问语法树中的所有元素节点
    visit(tree, "element", ((node: Element) => {
      // 只处理特定标签的元素
      if (
        ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "strong"].includes(
          node.tagName,
        ) &&
        node.children
      ) {
        // 创建新的子元素数组
        const newChildren: Array<ElementContent> = [];
        
        // 遍历当前节点的所有子元素
        node.children.forEach((child) => {
          // 如果子元素是文本节点
          if (child.type === "text") {
            // 使用Intl.Segmenter进行中文分词
            const segmenter = new Intl.Segmenter("zh", { granularity: "word" });
            // 对文本进行分词
            const segments = segmenter.segment(child.value);
            // 将分词结果转换为数组并过滤空值
            const words = Array.from(segments)
              .map((segment) => segment.segment)
              .filter(Boolean);
            
            // 为每个词创建一个带有动画效果的span元素
            words.forEach((word: string) => {
              newChildren.push({
                type: "element",
                tagName: "span",
                properties: {
                  className: "animate-fade-in", // 添加淡入动画类名
                },
                children: [{ type: "text", value: word }], // 将词作为文本节点
              });
            });
          } else {
            // 如果不是文本节点，直接保留
            newChildren.push(child);
          }
        });
        
        // 用新的子元素数组替换原来的子元素
        node.children = newChildren;
      }
    }) as BuildVisitor<Root, "element">);
  };
}
