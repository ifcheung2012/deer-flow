// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入Zod验证库
import { z } from "zod";

/**
 * MCP配置模式定义
 * 使用Zod库定义MCP服务器配置的验证模式
 * 包含两种类型的服务器配置：命令行(stdio)和URL(sse)
 */
export const MCPConfigSchema = z.object({
  // MCP服务器配置记录，键为服务器名称，值为配置对象
  mcpServers: z.record(
    // 联合类型，支持两种服务器配置
    z.union(
      [
        // 命令行(stdio)服务器配置
        z.object({
          // 执行命令
          command: z.string({
            message: "`command` must be a string",
          }),
          // 可选的命令参数数组
          args: z
            .array(z.string(), {
              message: "`args` must be an array of strings",
            })
            .optional(),
          // 可选的环境变量对象
          env: z
            .record(z.string(), {
              message: "`env` must be an object of key-value pairs",
            })
            .optional(),
        }),
        // URL(sse)服务器配置
        z.object({
          // 服务器URL，必须是有效的HTTP或HTTPS URL
          url: z
            .string({
              message:
                "`url` must be a valid URL starting with http:// or https://",
            })
            // 自定义验证，确保URL格式正确且使用HTTP或HTTPS协议
            .refine(
              (value) => {
                try {
                  const url = new URL(value);
                  return url.protocol === "http:" || url.protocol === "https:";
                } catch {
                  return false;
                }
              },
              {
                message:
                  "`url` must be a valid URL starting with http:// or https://",
              },
            ),
          // 可选的环境变量对象
          env: z
            .record(z.string(), {
              message: "`env` must be an object of key-value pairs",
            })
            .optional(),
        }),
      ],
      {
        message: "Invalid server type", // 无效服务器类型错误消息
      },
    ),
  ),
});
