"use client"; // 指示这是一个客户端组件

import { ThemeProvider as NextThemesProvider } from "next-themes";
import * as React from "react";

/**
 * 主题提供者组件
 * 包装next-themes的ThemeProvider，为应用提供主题支持
 * 
 * @param {React.ComponentProps<typeof NextThemesProvider>} props - 组件属性，与NextThemesProvider相同
 * @returns {React.ReactNode} 包装了主题提供者的子组件
 */
export function ThemeProvider({
  children, // 子组件
  ...props // 其他属性，传递给NextThemesProvider
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
