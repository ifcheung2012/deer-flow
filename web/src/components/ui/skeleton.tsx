import { cn } from "~/lib/utils"

/**
 * 骨架屏组件
 * 用于在内容加载过程中显示占位符，提供更好的用户体验
 * 
 * @param {Object} props - 组件属性
 * @param {string} props.className - 自定义CSS类名
 * @returns {React.ReactElement} 骨架屏元素
 */
function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="skeleton" // 数据属性，用于标识组件
      className={cn("bg-accent animate-pulse rounded-md", className)} // 应用动画和样式
      {...props} // 传递其他属性
    />
  )
}

export { Skeleton }
