/**
 * Markdown自动修复工具
 * 用于修复不完整或格式错误的Markdown文本
 * 
 * @param {string} markdown - 需要修复的Markdown文本
 * @returns {string} 修复后的Markdown文本
 */
export function autoFixMarkdown(markdown: string): string {
  return autoCloseTrailingLink(markdown);
}

/**
 * 自动闭合未闭合的Markdown链接或图片语法
 * 处理各种未闭合的情况，如缺少括号、方括号等
 * 
 * @param {string} markdown - 需要修复的Markdown文本
 * @returns {string} 修复后的Markdown文本
 */
function autoCloseTrailingLink(markdown: string): string {
  // 修复未闭合的Markdown链接或图片
  let fixedMarkdown: string = markdown;

  // 修复未闭合的图片语法 ![...](...)
  fixedMarkdown = fixedMarkdown.replace(
    /!\[([^\]]*)\]\(([^)]*)$/g,
    (match: string, altText: string, url: string): string => {
      return `![${altText}](${url})`;
    },
  );

  // 修复未闭合的链接语法 [...](...)
  fixedMarkdown = fixedMarkdown.replace(
    /\[([^\]]*)\]\(([^)]*)$/g,
    (match: string, linkText: string, url: string): string => {
      return `[${linkText}](${url})`;
    },
  );

  // 修复未闭合的图片语法 ![...]
  fixedMarkdown = fixedMarkdown.replace(
    /!\[([^\]]*)$/g,
    (match: string, altText: string): string => {
      return `![${altText}]`;
    },
  );

  // 修复未闭合的链接语法 [...]
  fixedMarkdown = fixedMarkdown.replace(
    /\[([^\]]*)$/g,
    (match: string, linkText: string): string => {
      return `[${linkText}]`;
    },
  );

  // 修复缺少")"的图片或链接
  fixedMarkdown = fixedMarkdown.replace(
    /!\[([^\]]*)\]\(([^)]*)$/g,
    (match: string, altText: string, url: string): string => {
      return `![${altText}](${url})`;
    },
  );

  // 修复缺少")"的链接
  fixedMarkdown = fixedMarkdown.replace(
    /\[([^\]]*)\]\(([^)]*)$/g,
    (match: string, linkText: string, url: string): string => {
      return `[${linkText}](${url})`;
    },
  );

  return fixedMarkdown;
}
