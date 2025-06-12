import * as React from "react"

const MOBILE_BREAKPOINT = 768

/**
 * 自定义Hook，用于检测当前设备是否为移动设备
 * 根据屏幕宽度判断，小于768px则认为是移动设备
 * @returns {boolean} 是否为移动设备
 */
export function useIsMobile() {
  // 状态用于存储是否为移动设备，初始值为undefined
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined)

  React.useEffect(() => {
    // 创建媒体查询，检测屏幕宽度是否小于移动设备断点
    const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`)
    
    // 定义媒体查询变化时的回调函数
    const onChange = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    }
    
    // 添加媒体查询变化事件监听器
    mql.addEventListener("change", onChange)
    
    // 初始化设置当前状态
    setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    
    // 组件卸载时移除事件监听器
    return () => mql.removeEventListener("change", onChange)
  }, []) // 空依赖数组，表示仅在组件挂载时执行一次

  // 返回结果，确保返回布尔值（!!将undefined转换为false）
  return !!isMobile
}
