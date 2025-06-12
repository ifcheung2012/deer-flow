# DeerFlow Web 界面设计

## 概述

DeerFlow Web 界面是一个基于 Next.js 构建的现代 Web 应用，提供直观、交互式的用户体验。该界面支持研究查询提交、研究计划审查、报告查看和编辑等功能，使用户能够充分利用 DeerFlow 的深度研究能力。

## 技术栈

- **前端框架**：Next.js 14+
- **UI 组件库**：Shadcn UI
- **状态管理**：Zustand
- **样式**：Tailwind CSS
- **编辑器**：Tiptap (基于 ProseMirror)
- **API 通信**：Fetch API

## 核心功能

### 1. 聊天界面

**功能**：
- 提交研究查询
- 查看研究进度
- 与系统进行交互式对话
- 接收和审查研究计划

**实现**：
- `web/src/app/chat/components/messages-block.tsx`：消息显示组件
- `web/src/app/chat/components/message-input.tsx`：消息输入组件

### 2. 研究报告界面

**功能**：
- 查看完整研究报告
- 编辑和修改报告内容
- AI 辅助润色和改进
- 导出报告为不同格式

**实现**：
- `web/src/app/chat/components/research-block.tsx`：研究报告显示组件
- `web/src/components/editor/`：基于 Tiptap 的编辑器组件

### 3. 设置界面

**功能**：
- 配置 LLM 模型参数
- 设置研究计划参数
- 管理 API 密钥
- 自定义界面偏好

**实现**：
- `web/src/app/settings/`：设置页面组件

## 界面布局

### 主布局

DeerFlow Web 界面采用响应式布局，适应不同屏幕尺寸：

```
┌─────────────────────────────────────────────────┐
│                    顶部导航                      │
├─────────────┬───────────────────────────────────┤
│             │                                   │
│             │                                   │
│   侧边栏    │            主内容区               │
│  (历史记录) │      (消息/研究报告显示)          │
│             │                                   │
│             │                                   │
├─────────────┴───────────────────────────────────┤
│                    底部输入                      │
└─────────────────────────────────────────────────┘
```

**实现**：
- `web/src/app/layout.tsx`：应用主布局
- `web/src/components/layout/`：布局组件

### 聊天界面布局

聊天界面采用双栏设计，左侧显示消息，右侧显示研究报告：

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│                     │                     │
│      消息区         │     研究报告区      │
│                     │                     │
│                     │                     │
│                     │                     │
├─────────────────────┴─────────────────────┤
│               消息输入区                  │
└───────────────────────────────────────────┘
```

**实现**：
- `web/src/app/chat/main.tsx`：聊天界面主组件

## 组件设计

### 1. 消息组件

**功能**：
- 显示用户和系统消息
- 支持 Markdown 渲染
- 显示代码块和表格
- 支持消息操作（复制、删除等）

**实现**：
```tsx
export function Message({ message, isLoading }: MessageProps) {
  const { role, content } = message;
  
  return (
    <div className={cn("message", role === "user" ? "user-message" : "ai-message")}>
      <div className="message-avatar">
        {role === "user" ? <UserIcon /> : <BotIcon />}
      </div>
      <div className="message-content">
        {isLoading ? (
          <MessageSkeleton />
        ) : (
          <MarkdownRenderer content={content} />
        )}
      </div>
      <div className="message-actions">
        <CopyButton text={content} />
        {/* 其他操作按钮 */}
      </div>
    </div>
  );
}
```

### 2. 编辑器组件

**功能**：
- 富文本编辑
- AI 辅助润色
- 块级编辑
- 导出为多种格式

**实现**：
```tsx
export function Editor({ content, onChange }: EditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      // 其他扩展...
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });
  
  return (
    <div className="editor-container">
      <EditorToolbar editor={editor} />
      <EditorContent editor={editor} />
      <AIAssistPanel editor={editor} />
    </div>
  );
}
```

### 3. 研究计划审查组件

**功能**：
- 显示生成的研究计划
- 提供接受或编辑选项
- 支持计划修改建议提交

**实现**：
```tsx
export function PlanReviewPanel({ plan, onAccept, onEdit }: PlanReviewProps) {
  const [feedback, setFeedback] = useState("");
  
  const handleAccept = () => {
    onAccept();
  };
  
  const handleEdit = () => {
    onEdit(`[EDIT_PLAN] ${feedback}`);
  };
  
  return (
    <div className="plan-review-panel">
      <h3>研究计划审查</h3>
      <div className="plan-content">
        <pre>{JSON.stringify(plan, null, 2)}</pre>
      </div>
      <div className="feedback-input">
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="输入修改建议..."
        />
      </div>
      <div className="action-buttons">
        <button onClick={handleAccept}>接受计划</button>
        <button onClick={handleEdit}>提交修改</button>
      </div>
    </div>
  );
}
```

## 状态管理

DeerFlow Web 界面使用 Zustand 进行状态管理：

```tsx
// web/src/core/store.ts
import { create } from 'zustand';

export const useStore = create((set) => ({
  // 聊天状态
  messages: [],
  isLoading: false,
  
  // 研究状态
  openResearchId: null,
  researches: {},
  
  // 设置状态
  settings: {
    maxPlanIterations: 1,
    maxStepNum: 3,
    autoAcceptedPlan: true,
  },
  
  // 操作方法
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  openResearch: (id) => set({ openResearchId: id }),
  
  updateSettings: (settings) => set((state) => ({
    settings: { ...state.settings, ...settings },
  })),
  
  // 其他状态和方法...
}));
```

## API 集成

DeerFlow Web 界面通过 API 与后端服务通信：

### 1. 消息 API

```tsx
// web/src/lib/api.ts
export async function sendMessage(message, threadId = "default") {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: [{ role: 'user', content: message }],
      thread_id: threadId,
      auto_accepted_plan: useStore.getState().settings.autoAcceptedPlan,
    }),
  });
  
  return response.json();
}
```

### 2. 流式响应处理

```tsx
// web/src/lib/stream.ts
export async function handleMessageStream(response, onChunk, onComplete) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    
    // 处理缓冲区中的完整消息
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') {
          onComplete();
          return;
        }
        
        try {
          const chunk = JSON.parse(data);
          onChunk(chunk);
        } catch (e) {
          console.error('Error parsing chunk:', e);
        }
      }
    }
  }
  
  onComplete();
}
```

## 响应式设计

DeerFlow Web 界面采用响应式设计，适应不同屏幕尺寸：

```tsx
// web/src/app/chat/main.tsx
export default function Main() {
  const openResearchId = useStore((state) => state.openResearchId);
  const doubleColumnMode = useMemo(
    () => openResearchId !== null,
    [openResearchId],
  );
  
  return (
    <div
      className={cn(
        "flex h-full w-full justify-center-safe px-4 pt-12 pb-4",
        doubleColumnMode && "gap-8",
      )}
    >
      <MessagesBlock
        className={cn(
          "shrink-0 transition-all duration-300 ease-out",
          !doubleColumnMode &&
            `w-[768px] translate-x-[min(max(calc((100vw-538px)*0.75),575px)/2,960px/2)]`,
          doubleColumnMode && `w-[538px]`,
        )}
      />
      <ResearchBlock
        className={cn(
          "w-[min(max(calc((100vw-538px)*0.75),575px),960px)] pb-4 transition-all duration-300 ease-out",
          !doubleColumnMode && "scale-0",
          doubleColumnMode && "",
        )}
        researchId={openResearchId}
      />
    </div>
  );
}
```

## 多媒体支持

DeerFlow Web 界面支持多种多媒体内容：

### 1. 播客音频生成

**功能**：
- 从研究报告生成播客音频
- 调整语音参数（速度、音量、音调）
- 下载和播放生成的音频

**实现**：
```tsx
export function PodcastGenerator({ content }: PodcastGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [settings, setSettings] = useState({
    speedRatio: 1.0,
    volumeRatio: 1.0,
    pitchRatio: 1.0,
  });
  
  const generatePodcast = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: content,
          ...settings,
        }),
      });
      
      const blob = await response.blob();
      setAudioUrl(URL.createObjectURL(blob));
    } catch (error) {
      console.error('Error generating podcast:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <div className="podcast-generator">
      <div className="settings">
        {/* 设置控件 */}
      </div>
      <button onClick={generatePodcast} disabled={isGenerating}>
        {isGenerating ? '生成中...' : '生成播客'}
      </button>
      {audioUrl && (
        <div className="audio-player">
          <audio controls src={audioUrl} />
          <a href={audioUrl} download="podcast.mp3">下载</a>
        </div>
      )}
    </div>
  );
}
```

### 2. 演示文稿生成

**功能**：
- 从研究报告生成简单的 PowerPoint 演示文稿
- 自定义模板和样式
- 下载生成的演示文稿

**实现**：
```tsx
export function PresentationGenerator({ content }: PresentationGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState("");
  
  const generatePresentation = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/ppt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          template: 'default',
        }),
      });
      
      const blob = await response.blob();
      setDownloadUrl(URL.createObjectURL(blob));
    } catch (error) {
      console.error('Error generating presentation:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <div className="presentation-generator">
      <button onClick={generatePresentation} disabled={isGenerating}>
        {isGenerating ? '生成中...' : '生成演示文稿'}
      </button>
      {downloadUrl && (
        <a href={downloadUrl} download="presentation.pptx">下载演示文稿</a>
      )}
    </div>
  );
}
```

## 用户体验优化

DeerFlow Web 界面实现了多项用户体验优化：

1. **加载状态指示器**：在数据加载和处理过程中显示进度
2. **渐进式渲染**：流式显示生成的内容，减少等待时间
3. **错误处理**：友好的错误提示和恢复机制
4. **键盘快捷键**：支持常用操作的键盘快捷键
5. **主题支持**：明暗模式切换
6. **本地存储**：保存用户偏好和历史记录

## 部署和构建

DeerFlow Web 界面支持多种部署方式：

1. **开发模式**：
   ```bash
   cd web
   pnpm install
   pnpm dev
   ```

2. **生产构建**：
   ```bash
   cd web
   pnpm build
   pnpm start
   ```

3. **Docker 部署**：
   ```bash
   docker compose up
   ```

## 扩展性设计

DeerFlow Web 界面的扩展性体现在：

1. **模块化组件**：组件设计遵循单一职责原则，便于替换和扩展
2. **插件系统**：支持编辑器插件和工具扩展
3. **主题定制**：支持自定义主题和样式
4. **国际化**：支持多语言界面
5. **API 抽象**：统一的 API 接口，便于切换后端服务 