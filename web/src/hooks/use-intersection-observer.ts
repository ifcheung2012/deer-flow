import { useEffect, useRef, useState } from "react";

// 定义状态类型接口
type State = {
  isIntersecting: boolean; // 是否相交
  entry?: IntersectionObserverEntry; // 相交观察器条目
};

// 定义使用相交观察器的选项接口
type UseIntersectionObserverOptions = {
  root?: Element | Document | null; // 根元素
  rootMargin?: string; // 根元素边距
  threshold?: number | number[]; // 触发阈值
  freezeOnceVisible?: boolean; // 一旦可见就冻结观察
  onChange?: (
    isIntersecting: boolean,
    entry: IntersectionObserverEntry,
  ) => void; // 状态变化回调
  initialIsIntersecting?: boolean; // 初始相交状态
};

// 定义返回类型，包含引用设置函数、是否相交状态和相交条目
type IntersectionReturn = [
  (node?: Element | null) => void,
  boolean,
  IntersectionObserverEntry | undefined,
] & {
  ref: (node?: Element | null) => void;
  isIntersecting: boolean;
  entry?: IntersectionObserverEntry;
};

/**
 * 使用相交观察器的自定义Hook
 * 用于检测元素是否进入视口
 */
export function useIntersectionObserver({
  threshold = 0,
  root = null,
  rootMargin = "0%",
  freezeOnceVisible = false,
  initialIsIntersecting = false,
  onChange,
}: UseIntersectionObserverOptions = {}): IntersectionReturn {
  // 存储被观察元素的引用
  const [ref, setRef] = useState<Element | null>(null);

  // 存储相交状态
  const [state, setState] = useState<State>(() => ({
    isIntersecting: initialIsIntersecting,
    entry: undefined,
  }));

  // 使用ref存储回调函数以避免不必要的重渲染
  const callbackRef =
    useRef<UseIntersectionObserverOptions["onChange"]>(undefined);

  callbackRef.current = onChange;

  // 如果元素已经相交且设置了冻结选项，则冻结观察
  const frozen = state.entry?.isIntersecting && freezeOnceVisible;

  useEffect(() => {
    // 确保有引用可以观察
    if (!ref) return;

    // 确保浏览器支持相交观察器API
    if (!("IntersectionObserver" in window)) return;

    // 如果已冻结则跳过
    if (frozen) return;

    let unobserve: (() => void) | undefined;

    // 创建相交观察器实例
    const observer = new IntersectionObserver(
      (entries: IntersectionObserverEntry[]): void => {
        // 获取观察器的阈值
        const thresholds = Array.isArray(observer.thresholds)
          ? observer.thresholds
          : [observer.thresholds];

        entries.forEach((entry) => {
          // 判断元素是否相交并且相交比例超过阈值
          const isIntersecting =
            entry.isIntersecting &&
            thresholds.some(
              (threshold) => entry.intersectionRatio >= threshold,
            );

          // 更新状态
          setState({ isIntersecting, entry });

          // 如果有回调函数，则调用
          if (callbackRef.current) {
            callbackRef.current(isIntersecting, entry);
          }

          // 如果元素相交且设置了冻结选项，则停止观察
          if (isIntersecting && freezeOnceVisible && unobserve) {
            unobserve();
            unobserve = undefined;
          }
        });
      },
      { threshold, root, rootMargin },
    );

    // 开始观察元素
    observer.observe(ref);

    // 清理函数，断开观察器连接
    return () => {
      observer.disconnect();
    };

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    ref,
    // eslint-disable-next-line react-hooks/exhaustive-deps
    JSON.stringify(threshold),
    root,
    rootMargin,
    frozen,
    freezeOnceVisible,
  ]);

  // 确保如果观察的元素改变，相交观察器会重新初始化
  const prevRef = useRef<Element | null>(null);

  useEffect(() => {
    if (
      !ref &&
      state.entry?.target &&
      !freezeOnceVisible &&
      !frozen &&
      prevRef.current !== state.entry.target
    ) {
      prevRef.current = state.entry.target;
      setState({ isIntersecting: initialIsIntersecting, entry: undefined });
    }
  }, [ref, state.entry, freezeOnceVisible, frozen, initialIsIntersecting]);

  // 构造返回结果
  const result = [
    setRef,
    !!state.isIntersecting,
    state.entry,
  ] as IntersectionReturn;

  // 支持对象解构，添加特定值
  result.ref = result[0];
  result.isIntersecting = result[1];
  result.entry = result[2];

  return result;
}
