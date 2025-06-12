// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client"; // 声明这是一个客户端组件

import { useMemo } from "react";

import { useStore } from "~/core/store";
import { cn } from "~/lib/utils";

import { MessagesBlock } from "./components/messages-block";
import { ResearchBlock } from "./components/research-block";

/**
 * 主内容区域组件
 * 包含消息区块和研究区块，支持双列模式
 * 
 * @returns {React.ReactElement} 主内容区域元素
 */
export default function Main() {
  // 获取当前打开的研究ID
  const openResearchId = useStore((state) => state.openResearchId);
  
  // 根据是否有打开的研究ID来决定是否启用双列模式
  const doubleColumnMode = useMemo(
    () => openResearchId !== null,
    [openResearchId],
  );
  
  return (
    <div
      className={cn(
        "flex h-full w-full justify-center-safe px-4 pt-12 pb-4",
        doubleColumnMode && "gap-8", // 双列模式时添加间距
      )}
    >
      {/* 消息区块 - 左侧 */}
      <MessagesBlock
        className={cn(
          "shrink-0 transition-all duration-300 ease-out",
          // 非双列模式时的宽度和位置
          !doubleColumnMode &&
            `w-[768px] translate-x-[min(max(calc((100vw-538px)*0.75),575px)/2,960px/2)]`,
          // 双列模式时的宽度
          doubleColumnMode && `w-[538px]`,
        )}
      />
      
      {/* 研究区块 - 右侧 */}
      <ResearchBlock
        className={cn(
          "w-[min(max(calc((100vw-538px)*0.75),575px),960px)] pb-4 transition-all duration-300 ease-out",
          !doubleColumnMode && "scale-0", // 非双列模式时隐藏
          doubleColumnMode && "", // 双列模式时显示
        )}
        researchId={openResearchId} // 传递研究ID
      />
    </div>
  );
}
