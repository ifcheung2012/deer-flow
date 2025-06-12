// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

// 导入环境变量处理相关库
import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  /**
   * Specify your server-side environment variables schema here. This way you can ensure the app
   * isn't built with invalid env vars.
   * 
   * 在此处指定服务器端环境变量模式。这样可以确保应用程序不会使用无效的环境变量构建。
   */
  server: {
    NODE_ENV: z.enum(["development", "test", "production"]), // 节点环境：开发、测试或生产
    AMPLITUDE_API_KEY: z.string().optional(), // Amplitude API密钥（可选）
    GITHUB_OAUTH_TOKEN: z.string().optional(), // GitHub OAuth令牌（可选）
  },

  /**
   * Specify your client-side environment variables schema here. This way you can ensure the app
   * isn't built with invalid env vars. To expose them to the client, prefix them with
   * `NEXT_PUBLIC_`.
   * 
   * 在此处指定客户端环境变量模式。这样可以确保应用程序不会使用无效的环境变量构建。
   * 要将它们暴露给客户端，请使用`NEXT_PUBLIC_`前缀。
   */
  client: {
    NEXT_PUBLIC_API_URL: z.string().optional(), // 公共API URL（可选）
    NEXT_PUBLIC_STATIC_WEBSITE_ONLY: z.boolean().optional(), // 是否仅为静态网站（可选）
  },

  /**
   * You can't destruct `process.env` as a regular object in the Next.js edge runtimes (e.g.
   * middlewares) or client-side so we need to destruct manually.
   * 
   * 在Next.js边缘运行时（如中间件）或客户端中，不能像常规对象一样解构`process.env`，
   * 因此我们需要手动解构。
   */
  runtimeEnv: {
    NODE_ENV: process.env.NODE_ENV,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_STATIC_WEBSITE_ONLY:
      process.env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true",
    AMPLITUDE_API_KEY: process.env.AMPLITUDE_API_KEY,
    GITHUB_OAUTH_TOKEN: process.env.GITHUB_OAUTH_TOKEN,
  },
  /**
   * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially
   * useful for Docker builds.
   * 
   * 使用`SKIP_ENV_VALIDATION`运行`build`或`dev`可跳过环境验证。
   * 这对Docker构建特别有用。
   */
  skipValidation: !!process.env.SKIP_ENV_VALIDATION,
  /**
   * Makes it so that empty strings are treated as undefined. `SOME_VAR: z.string()` and
   * `SOME_VAR=''` will throw an error.
   * 
   * 使空字符串被视为未定义。`SOME_VAR: z.string()`和`SOME_VAR=''`将抛出错误。
   */
  emptyStringAsUndefined: true,
});
