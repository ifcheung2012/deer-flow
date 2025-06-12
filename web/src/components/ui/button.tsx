import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "~/lib/utils";

/**
 * 按钮样式变体定义
 * 使用class-variance-authority库管理不同变体的样式
 */
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90", // 默认样式
        destructive:
          "bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60", // 破坏性操作样式
        outline:
          "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50", // 轮廓样式
        secondary:
          "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80", // 次要样式
        ghost:
          "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50", // 幽灵样式
        link: "text-primary underline-offset-4 hover:underline", // 链接样式
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3", // 默认尺寸
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5", // 小尺寸
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4", // 大尺寸
        icon: "size-9", // 图标尺寸
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

/**
 * 按钮组件
 * 支持多种变体和尺寸，可以作为子元素渲染
 * 
 * @param {Object} props - 组件属性
 * @param {string} props.className - 自定义CSS类名
 * @param {string} props.variant - 按钮变体（样式）
 * @param {string} props.size - 按钮尺寸
 * @param {boolean} props.asChild - 是否作为子元素渲染
 * @returns {React.ReactElement} 按钮元素
 */
function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  // 如果asChild为true，则使用Slot组件，否则使用button元素
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      data-slot="button" // 数据属性，用于标识组件
      className={cn(
        buttonVariants({ variant, size, className }), // 应用按钮变体样式
        "cursor-pointer active:scale-105", // 添加指针样式和点击效果
      )}
      {...props} // 传递其他属性
    />
  );
}

export { Button, buttonVariants };
