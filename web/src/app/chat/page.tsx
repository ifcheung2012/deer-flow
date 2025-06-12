// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client"; // 声明这是一个客户端组件

import { GithubOutlined } from "@ant-design/icons";
import dynamic from "next/dynamic";
import Link from "next/link";
import { Suspense } from "react";

import { Button } from "~/components/ui/button";

import { Logo } from "../../components/deer-flow/logo";
import { ThemeToggle } from "../../components/deer-flow/theme-toggle";
import { Tooltip } from "../../components/deer-flow/tooltip";
import { SettingsDialog } from "../settings/dialogs/settings-dialog";

/**
 * 动态导入主要内容组件
 * 使用Next.js的dynamic函数实现客户端渲染
 * 禁用服务器端渲染(SSR)并提供加载状态
 */
const Main = dynamic(() => import("./main"), {
  ssr: false, // 禁用服务器端渲染
  loading: () => (
    // 加载状态显示
    <div className="flex h-full w-full items-center justify-center">
      Loading DeerFlow...
    </div>
  ),
});

/**
 * 聊天页面组件
 * 包含页面头部导航和主要内容区域
 * 
 * @returns {React.ReactElement} 聊天页面元素
 */
export default function HomePage() {
  return (
    <div className="flex h-screen w-screen justify-center overscroll-none">
      {/* 页面头部导航 */}
      <header className="fixed top-0 left-0 flex h-12 w-full items-center justify-between px-4">
        {/* 左侧Logo */}
        <Logo />
        {/* 右侧工具栏 */}
        <div className="flex items-center">
          {/* GitHub链接 */}
          <Tooltip title="Star DeerFlow on GitHub">
            <Button variant="ghost" size="icon" asChild>
              <Link
                href="https://github.com/bytedance/deer-flow"
                target="_blank"
              >
                <GithubOutlined />
              </Link>
            </Button>
          </Tooltip>
          {/* 主题切换按钮 */}
          <ThemeToggle />
          {/* 设置对话框 - 使用Suspense包裹以处理异步加载 */}
          <Suspense>
            <SettingsDialog />
          </Suspense>
        </div>
      </header>
      {/* 主要内容区域 */}
      <Main />
    </div>
  );
}
