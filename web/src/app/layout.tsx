// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入全局样式
import "~/styles/globals.css";

// 导入Next.js相关组件和类型
import { type Metadata } from "next";
import { Geist } from "next/font/google";
import Script from "next/script";

// 导入自定义组件
import { ThemeProviderWrapper } from "~/components/deer-flow/theme-provider-wrapper";
import { env } from "~/env";

import { Toaster } from "../components/deer-flow/toaster";

// 定义网站元数据
export const metadata: Metadata = {
  title: "🦌 DeerFlow",
  description:
    "Deep Exploration and Efficient Research, an AI tool that combines language models with specialized tools for research tasks.",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

// 配置Geist字体
const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

/**
 * 根布局组件
 * 为整个应用提供基础布局结构
 * 
 * @param {Object} props - 组件属性
 * @param {React.ReactNode} props.children - 子组件
 * @returns {React.ReactElement} 根布局元素
 */
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geist.variable}`} suppressHydrationWarning>
      <head>
        {/* 
          全局定义isSpace函数以修复markdown-it在Next.js + Turbopack环境下的问题
          参考：https://github.com/markdown-it/markdown-it/issues/1082#issuecomment-2749656365 
        */}
        <Script id="markdown-it-fix" strategy="beforeInteractive">
          {`
            if (typeof window !== 'undefined' && typeof window.isSpace === 'undefined') {
              window.isSpace = function(code) {
                return code === 0x20 || code === 0x09 || code === 0x0A || code === 0x0B || code === 0x0C || code === 0x0D;
              };
            }
          `}
        </Script>
      </head>
      <body className="bg-app">
        {/* 主题提供者包装器，为应用提供主题支持 */}
        <ThemeProviderWrapper>{children}</ThemeProviderWrapper>
        {/* 消息提示组件 */}
        <Toaster />
        {
          // 默认情况下不跟踪用户行为或收集私人数据
          //
          // 当`NEXT_PUBLIC_STATIC_WEBSITE_ONLY`为`true`时，
          // 只有在`.env`中提供了`AMPLITUDE_API_KEY`时才会将脚本注入页面
        }
        {env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY && env.AMPLITUDE_API_KEY && (
          <>
            {/* Amplitude分析脚本 */}
            <Script src="https://cdn.amplitude.com/script/d2197dd1df3f2959f26295bb0e7e849f.js"></Script>
            <Script id="amplitude-init" strategy="lazyOnload">
              {`window.amplitude.init('${env.AMPLITUDE_API_KEY}', {"fetchRemoteConfig":true,"autocapture":true});`}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}
