/**
 * Markdown文件声明模块
 * 允许TypeScript正确处理导入的.md文件
 * 将.md文件内容作为字符串导入
 */
declare module "*.md" {
  const content: string; // 文件内容作为字符串
  export default content;
}
