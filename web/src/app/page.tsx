// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入React钩子
import { useMemo } from "react";

// 导入页面组件
import { SiteHeader } from "./chat/components/site-header";
import { Jumbotron } from "./landing/components/jumbotron";
import { Ray } from "./landing/components/ray";
import { CaseStudySection } from "./landing/sections/case-study-section";
import { CoreFeatureSection } from "./landing/sections/core-features-section";
import { JoinCommunitySection } from "./landing/sections/join-community-section";
import { MultiAgentSection } from "./landing/sections/multi-agent-section";

/**
 * 首页组件
 * 包含网站的主要着陆页内容
 * 
 * @returns {React.ReactElement} 首页元素
 */
export default function HomePage() {
  return (
    <div className="flex flex-col items-center">
      {/* 网站头部导航 */}
      <SiteHeader />
      <main className="container flex flex-col items-center justify-center gap-56">
        {/* 大型横幅展示区 */}
        <Jumbotron />
        {/* 案例研究部分 */}
        <CaseStudySection />
        {/* 多代理部分 */}
        <MultiAgentSection />
        {/* 核心功能部分 */}
        <CoreFeatureSection />
        {/* 加入社区部分 */}
        <JoinCommunitySection />
      </main>
      {/* 页脚 */}
      <Footer />
      {/* 光线效果组件 */}
      <Ray />
    </div>
  );
}

/**
 * 页脚组件
 * 显示版权信息和许可证声明
 * 
 * @returns {React.ReactElement} 页脚元素
 */
function Footer() {
  // 使用useMemo缓存当前年份，避免不必要的重新计算
  const year = useMemo(() => new Date().getFullYear(), []);
  return (
    <footer className="container mt-32 flex flex-col items-center justify-center">
      {/* 分隔线 */}
      <hr className="from-border/0 via-border/70 to-border/0 m-0 h-px w-full border-none bg-gradient-to-r" />
      <div className="text-muted-foreground container flex h-20 flex-col items-center justify-center text-sm">
        {/* 引用语 */}
        <p className="text-center font-serif text-lg md:text-xl">
          &quot;Originated from Open Source, give back to Open Source.&quot;
        </p>
      </div>
      <div className="text-muted-foreground container mb-8 flex flex-col items-center justify-center text-xs">
        {/* 许可证信息 */}
        <p>Licensed under MIT License</p>
        {/* 版权信息 */}
        <p>&copy; {year} DeerFlow</p>
      </div>
    </footer>
  );
}
