// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Settings } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Tooltip } from "~/components/deer-flow/tooltip";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "~/components/ui/dialog";
import { Tabs, TabsContent } from "~/components/ui/tabs";
import { useReplay } from "~/core/replay";
import {
  type SettingsState,
  changeSettings,
  saveSettings,
  useSettingsStore,
} from "~/core/store";
import { cn } from "~/lib/utils";

import { SETTINGS_TABS } from "../tabs";

/**
 * 设置对话框组件
 * 提供应用程序设置的管理界面
 * 
 * @returns {React.ReactElement | null} 设置对话框元素或null（回放模式下）
 */
export function SettingsDialog() {
  // 检查是否处于回放模式
  const { isReplay } = useReplay();
  
  // 状态管理
  const [activeTabId, setActiveTabId] = useState(SETTINGS_TABS[0]!.id); // 当前活动选项卡
  const [open, setOpen] = useState(false); // 对话框是否打开
  const [settings, setSettings] = useState(useSettingsStore.getState()); // 当前设置
  const [changes, setChanges] = useState<Partial<SettingsState>>({}); // 未保存的更改

  /**
   * 处理选项卡内容变更
   * 将选项卡组件的更改添加到未保存更改中
   * 
   * @param {Partial<SettingsState>} newChanges - 新的设置更改
   */
  const handleTabChange = useCallback(
    (newChanges: Partial<SettingsState>) => {
      setTimeout(() => {
        if (open) {
          setChanges((prev) => ({
            ...prev,
            ...newChanges,
          }));
        }
      }, 0);
    },
    [open],
  );

  /**
   * 处理保存按钮点击
   * 应用所有更改并保存到存储
   */
  const handleSave = useCallback(() => {
    if (Object.keys(changes).length > 0) {
      const newSettings: SettingsState = {
        ...settings,
        ...changes,
      };
      setSettings(newSettings);
      setChanges({});
      changeSettings(newSettings);
      saveSettings();
    }
    setOpen(false);
  }, [settings, changes]);

  /**
   * 处理对话框打开
   * 从存储中获取最新设置
   */
  const handleOpen = useCallback(() => {
    setSettings(useSettingsStore.getState());
  }, []);

  /**
   * 处理对话框关闭
   * 清除未保存的更改
   */
  const handleClose = useCallback(() => {
    setChanges({});
  }, []);

  // 当对话框打开/关闭状态变化时执行相应处理
  useEffect(() => {
    if (open) {
      handleOpen();
    } else {
      handleClose();
    }
  }, [open, handleOpen, handleClose]);

  // 合并当前设置和未保存的更改
  const mergedSettings = useMemo<SettingsState>(() => {
    return {
      ...settings,
      ...changes,
    };
  }, [settings, changes]);

  // 在回放模式下不渲染组件
  if (isReplay) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {/* 设置按钮触发器 */}
      <Tooltip title="Settings">
        <DialogTrigger asChild>
          <Button variant="ghost" size="icon">
            <Settings />
          </Button>
        </DialogTrigger>
      </Tooltip>
      
      {/* 对话框内容 */}
      <DialogContent className="sm:max-w-[850px]">
        {/* 对话框标题和描述 */}
        <DialogHeader>
          <DialogTitle>DeerFlow Settings</DialogTitle>
          <DialogDescription>
            Manage your DeerFlow settings here.
          </DialogDescription>
        </DialogHeader>
        
        {/* 设置选项卡 */}
        <Tabs value={activeTabId}>
          <div className="flex h-120 w-full overflow-auto border-y">
            {/* 左侧选项卡列表 */}
            <ul className="flex w-50 shrink-0 border-r p-1">
              <div className="size-full">
                {SETTINGS_TABS.map((tab) => (
                  <li
                    key={tab.id}
                    className={cn(
                      "hover:accent-foreground hover:bg-accent mb-1 flex h-8 w-full cursor-pointer items-center gap-1.5 rounded px-2",
                      activeTabId === tab.id &&
                        "!bg-primary !text-primary-foreground",
                    )}
                    onClick={() => setActiveTabId(tab.id)}
                  >
                    <tab.icon size={16} />
                    <span>{tab.label}</span>
                    {tab.badge && (
                      <Badge
                        variant="outline"
                        className={cn(
                          "border-muted-foreground text-muted-foreground ml-auto px-1 py-0 text-xs",
                          activeTabId === tab.id &&
                            "border-primary-foreground text-primary-foreground",
                        )}
                      >
                        {tab.badge}
                      </Badge>
                    )}
                  </li>
                ))}
              </div>
            </ul>
            
            {/* 右侧选项卡内容 */}
            <div className="min-w-0 flex-grow">
              <div
                id="settings-content-scrollable"
                className="size-full overflow-auto p-4"
              >
                {SETTINGS_TABS.map((tab) => (
                  <TabsContent key={tab.id} value={tab.id}>
                    <tab.component
                      settings={mergedSettings}
                      onChange={handleTabChange}
                    />
                  </TabsContent>
                ))}
              </div>
            </div>
          </div>
        </Tabs>
        
        {/* 对话框底部按钮 */}
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button className="w-24" type="submit" onClick={handleSave}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
