// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入状态管理库
import { create } from "zustand";

// 导入MCP服务器元数据类型
import type { MCPServerMetadata, SimpleMCPServerMetadata } from "../mcp";

// 本地存储设置的键名
const SETTINGS_KEY = "deerflow.settings";

// 默认设置
const DEFAULT_SETTINGS: SettingsState = {
  general: {
    autoAcceptedPlan: false, // 自动接受计划
    enableBackgroundInvestigation: false, // 启用背景调查
    maxPlanIterations: 1, // 最大计划迭代次数
    maxStepNum: 3, // 最大步骤数
    maxSearchResults: 3, // 最大搜索结果数
    reportStyle: "academic", // 报告风格：学术
  },
  mcp: {
    servers: [], // MCP服务器列表
  },
};

/**
 * 设置状态类型定义
 */
export type SettingsState = {
  general: {
    autoAcceptedPlan: boolean; // 是否自动接受计划
    enableBackgroundInvestigation: boolean; // 是否启用背景调查
    maxPlanIterations: number; // 最大计划迭代次数
    maxStepNum: number; // 最大步骤数
    maxSearchResults: number; // 最大搜索结果数
    reportStyle: "academic" | "popular_science" | "news" | "social_media"; // 报告风格
  };
  mcp: {
    servers: MCPServerMetadata[]; // MCP服务器元数据数组
  };
};

/**
 * 创建设置状态存储
 * 使用zustand管理设置状态
 */
export const useSettingsStore = create<SettingsState>(() => ({
  ...DEFAULT_SETTINGS,
}));

/**
 * 获取特定设置分类的钩子
 * @param {keyof SettingsState} key - 设置分类键
 * @returns {SettingsState[keyof SettingsState]} 对应分类的设置
 */
export const useSettings = (key: keyof SettingsState) => {
  return useSettingsStore((state) => state[key]);
};

/**
 * 更改设置
 * @param {SettingsState} settings - 新的设置状态
 */
export const changeSettings = (settings: SettingsState) => {
  useSettingsStore.setState(settings);
};

/**
 * 从本地存储加载设置
 * 如果某些设置不存在，则使用默认值
 */
export const loadSettings = () => {
  // 检查是否在浏览器环境
  if (typeof window === "undefined") {
    return;
  }
  // 从本地存储获取设置
  const json = localStorage.getItem(SETTINGS_KEY);
  if (json) {
    const settings = JSON.parse(json);
    // 确保所有默认设置字段都存在
    for (const key in DEFAULT_SETTINGS.general) {
      if (!(key in settings.general)) {
        settings.general[key as keyof SettingsState["general"]] =
          DEFAULT_SETTINGS.general[key as keyof SettingsState["general"]];
      }
    }

    try {
      // 更新状态存储
      useSettingsStore.setState(settings);
    } catch (error) {
      console.error(error);
    }
  }
};

/**
 * 保存设置到本地存储
 */
export const saveSettings = () => {
  const latestSettings = useSettingsStore.getState();
  const json = JSON.stringify(latestSettings);
  localStorage.setItem(SETTINGS_KEY, json);
};

/**
 * 获取聊天流设置
 * 包括一般设置和MCP服务器配置
 * 
 * @returns {Object} 聊天流设置对象
 */
export const getChatStreamSettings = () => {
  // MCP设置初始为undefined
  let mcpSettings:
    | {
        servers: Record<
          string,
          MCPServerMetadata & {
            enabled_tools: string[];
            add_to_agents: string[];
          }
        >;
      }
    | undefined = undefined;
  
  // 获取当前设置状态
  const { mcp, general } = useSettingsStore.getState();
  // 过滤启用的MCP服务器
  const mcpServers = mcp.servers.filter((server) => server.enabled);
  
  if (mcpServers.length > 0) {
    // 构建MCP设置对象
    mcpSettings = {
      servers: mcpServers.reduce((acc, cur) => {
        const { transport, env } = cur;
        let server: SimpleMCPServerMetadata;
        // 根据传输类型构建服务器配置
        if (transport === "stdio") {
          server = {
            name: cur.name,
            transport,
            env,
            command: cur.command,
            args: cur.args,
          };
        } else {
          server = {
            name: cur.name,
            transport,
            env,
            url: cur.url,
          };
        }
        return {
          ...acc,
          [cur.name]: {
            ...server,
            enabled_tools: cur.tools.map((tool) => tool.name), // 启用的工具
            add_to_agents: ["researcher"], // 添加到代理
          },
        };
      }, {}),
    };
  }
  return {
    ...general,
    mcpSettings,
  };
};

/**
 * 设置报告风格
 * 
 * @param {"academic" | "popular_science" | "news" | "social_media"} value - 报告风格
 */
export function setReportStyle(value: "academic" | "popular_science" | "news" | "social_media") {
  useSettingsStore.setState((state) => ({
    general: {
      ...state.general,
      reportStyle: value,
    },
  }));
  saveSettings();
}

/**
 * 设置是否启用背景调查
 * 
 * @param {boolean} value - 是否启用
 */
export function setEnableBackgroundInvestigation(value: boolean) {
  useSettingsStore.setState((state) => ({
    general: {
      ...state.general,
      enableBackgroundInvestigation: value,
    },
  }));
  saveSettings();
}

// 初始加载设置
loadSettings();
