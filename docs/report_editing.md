# DeerFlow 报告编辑功能

## 概述

DeerFlow 的报告编辑功能允许用户在自动生成的研究报告基础上进行编辑、润色和定制，使最终输出更符合用户需求。本文档详细介绍报告编辑功能的特性、实现方式和最佳实践。

## 编辑器功能

### 富文本编辑

DeerFlow 集成了基于 [Tiptap](https://tiptap.dev/) 的富文本编辑器，提供类似 Notion 的编辑体验：

- **文本格式化**：支持粗体、斜体、下划线、高亮等格式
- **标题层级**：支持多级标题（H1-H6）
- **列表**：支持有序列表、无序列表和任务列表
- **表格**：支持创建和编辑表格
- **代码块**：支持带语法高亮的代码块
- **引用**：支持块引用和内联引用
- **链接**：支持添加和编辑超链接
- **图片**：支持插入和调整图片

### 块级编辑

DeerFlow 支持块级内容编辑，使报告结构调整更加便捷：

- **块选择**：选择特定内容块进行操作
- **块移动**：拖放方式调整块的位置
- **块复制**：复制现有块创建新内容
- **块删除**：删除不需要的内容块
- **块转换**：将一种块类型转换为另一种（如段落转列表）

### AI 辅助编辑

DeerFlow 提供 AI 辅助编辑功能，帮助用户改进报告内容：

- **内容润色**：改进语言表达和流畅度
- **内容扩展**：扩展简短段落，添加更多细节
- **内容精简**：精简冗长内容，保持核心信息
- **语法修正**：修正语法和拼写错误
- **风格调整**：调整内容风格（如学术、商业、新闻等）

## 技术实现

### 编辑器组件

DeerFlow 的编辑器基于 Tiptap 实现，集成在 Web 界面中：

```tsx
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import Image from '@tiptap/extension-image';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { lowlight } from 'lowlight';

export function ReportEditor({ content, onChange }) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableCell,
      TableHeader,
      Image,
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      CodeBlockLowlight.configure({
        lowlight,
      }),
      // 其他扩展...
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  return (
    <div className="report-editor">
      <EditorToolbar editor={editor} />
      <EditorContent editor={editor} />
    </div>
  );
}
```

### 工具栏实现

编辑器工具栏提供各种编辑功能：

```tsx
export function EditorToolbar({ editor }) {
  if (!editor) {
    return null;
  }

  return (
    <div className="editor-toolbar">
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={editor.isActive('bold') ? 'is-active' : ''}
      >
        粗体
      </button>
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={editor.isActive('italic') ? 'is-active' : ''}
      >
        斜体
      </button>
      {/* 更多工具栏按钮... */}
      
      <select
        onChange={(e) => {
          const level = parseInt(e.target.value);
          if (level === 0) {
            editor.chain().focus().setParagraph().run();
          } else {
            editor.chain().focus().toggleHeading({ level }).run();
          }
        }}
      >
        <option value="0">正文</option>
        <option value="1">标题 1</option>
        <option value="2">标题 2</option>
        <option value="3">标题 3</option>
        <option value="4">标题 4</option>
        <option value="5">标题 5</option>
        <option value="6">标题 6</option>
      </select>
      
      {/* 更多下拉菜单和选项... */}
    </div>
  );
}
```

### AI 辅助面板

AI 辅助编辑功能通过侧边面板实现：

```tsx
export function AIAssistPanel({ editor }) {
  const [isLoading, setIsLoading] = useState(false);
  
  const applyAIEdit = async (action) => {
    if (!editor) return;
    
    const selection = editor.state.selection;
    const selectedText = selection.empty 
      ? null 
      : editor.state.doc.textBetween(selection.from, selection.to);
    
    if (!selectedText) {
      alert('请先选择要编辑的文本');
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await fetch('/api/ai-edit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: selectedText,
          action,
        }),
      });
      
      const { result } = await response.json();
      
      editor
        .chain()
        .focus()
        .deleteRange({ from: selection.from, to: selection.to })
        .insertContent(result)
        .run();
    } catch (error) {
      console.error('AI 编辑错误:', error);
      alert('AI 编辑失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="ai-assist-panel">
      <h3>AI 辅助编辑</h3>
      <div className="ai-actions">
        <button 
          onClick={() => applyAIEdit('polish')} 
          disabled={isLoading}
        >
          润色内容
        </button>
        <button 
          onClick={() => applyAIEdit('expand')} 
          disabled={isLoading}
        >
          扩展内容
        </button>
        <button 
          onClick={() => applyAIEdit('shorten')} 
          disabled={isLoading}
        >
          精简内容
        </button>
        <button 
          onClick={() => applyAIEdit('fix-grammar')} 
          disabled={isLoading}
        >
          修正语法
        </button>
        <button 
          onClick={() => applyAIEdit('academic-style')} 
          disabled={isLoading}
        >
          学术风格
        </button>
        <button 
          onClick={() => applyAIEdit('business-style')} 
          disabled={isLoading}
        >
          商业风格
        </button>
      </div>
      {isLoading && <div className="loading-indicator">处理中...</div>}
    </div>
  );
}
```

### 服务器端 AI 编辑实现

AI 辅助编辑在服务器端的实现：

```python
@router.post("/ai-edit")
async def ai_edit(request: Request):
    data = await request.json()
    text = data.get("text")
    action = data.get("action")
    
    if not text or not action:
        return JSONResponse(
            status_code=400,
            content={"error": "缺少必要参数"}
        )
    
    # 根据不同操作构建提示
    prompts = {
        "polish": f"请润色以下文本，提高其表达质量和流畅度，但保持原意不变：\n\n{text}",
        "expand": f"请扩展以下文本，添加更多细节和解释，使其更加全面：\n\n{text}",
        "shorten": f"请精简以下文本，保留核心信息，减少冗余内容：\n\n{text}",
        "fix-grammar": f"请修正以下文本中的语法和拼写错误：\n\n{text}",
        "academic-style": f"请将以下文本改写为学术风格：\n\n{text}",
        "business-style": f"请将以下文本改写为商业报告风格：\n\n{text}",
    }
    
    prompt = prompts.get(action)
    if not prompt:
        return JSONResponse(
            status_code=400,
            content={"error": "不支持的操作类型"}
        )
    
    try:
        # 使用 LLM 处理文本
        llm = get_llm_by_type("basic")
        result = await llm.ainvoke([{"role": "user", "content": prompt}])
        
        return {"result": result.content}
    except Exception as e:
        logger.error(f"AI 编辑错误: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "处理请求时发生错误"}
        )
```

## 报告导出功能

### 支持的导出格式

DeerFlow 支持将编辑后的报告导出为多种格式：

- **Markdown**：纯文本 Markdown 格式
- **HTML**：完整 HTML 文档
- **PDF**：格式化 PDF 文档
- **Word**：Microsoft Word 文档 (.docx)

### 导出实现

报告导出功能的前端实现：

```tsx
export function ExportPanel({ content }) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState('markdown');
  
  const handleExport = async () => {
    setIsExporting(true);
    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          format: exportFormat,
        }),
      });
      
      if (!response.ok) {
        throw new Error('导出失败');
      }
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      // 创建下载链接
      const a = document.createElement('a');
      a.href = url;
      a.download = `research-report.${getFileExtension(exportFormat)}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('导出错误:', error);
      alert('导出失败，请稍后重试');
    } finally {
      setIsExporting(false);
    }
  };
  
  const getFileExtension = (format) => {
    switch (format) {
      case 'markdown': return 'md';
      case 'html': return 'html';
      case 'pdf': return 'pdf';
      case 'word': return 'docx';
      default: return 'txt';
    }
  };
  
  return (
    <div className="export-panel">
      <h3>导出报告</h3>
      <div className="export-options">
        <select 
          value={exportFormat}
          onChange={(e) => setExportFormat(e.target.value)}
        >
          <option value="markdown">Markdown</option>
          <option value="html">HTML</option>
          <option value="pdf">PDF</option>
          <option value="word">Word</option>
        </select>
        <button 
          onClick={handleExport}
          disabled={isExporting}
        >
          {isExporting ? '导出中...' : '导出'}
        </button>
      </div>
    </div>
  );
}
```

## 版本历史

### 版本管理功能

DeerFlow 提供简单的版本管理功能，帮助用户追踪报告的编辑历史：

- **自动保存**：定期自动保存编辑内容
- **版本列表**：显示编辑历史版本列表
- **版本比较**：比较不同版本的差异
- **版本恢复**：恢复到之前的版本

### 版本历史组件

```tsx
export function VersionHistory({ reportId, onRestore }) {
  const [versions, setVersions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const fetchVersions = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`/api/reports/${reportId}/versions`);
        const data = await response.json();
        setVersions(data.versions);
      } catch (error) {
        console.error('获取版本历史失败:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchVersions();
  }, [reportId]);
  
  const handleRestore = async (versionId) => {
    try {
      const response = await fetch(`/api/reports/${reportId}/restore`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          version_id: versionId,
        }),
      });
      
      if (!response.ok) {
        throw new Error('恢复版本失败');
      }
      
      const data = await response.json();
      onRestore(data.content);
    } catch (error) {
      console.error('恢复版本失败:', error);
      alert('恢复版本失败，请稍后重试');
    }
  };
  
  if (isLoading) {
    return <div>加载版本历史...</div>;
  }
  
  return (
    <div className="version-history">
      <h3>版本历史</h3>
      {versions.length === 0 ? (
        <p>暂无历史版本</p>
      ) : (
        <ul className="version-list">
          {versions.map((version) => (
            <li key={version.id} className="version-item">
              <div className="version-info">
                <span className="version-time">
                  {new Date(version.created_at).toLocaleString()}
                </span>
                {version.is_current && (
                  <span className="current-badge">当前版本</span>
                )}
              </div>
              <div className="version-actions">
                <button 
                  onClick={() => handleRestore(version.id)}
                  disabled={version.is_current}
                >
                  恢复此版本
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

## 协作编辑

### 未来协作功能

DeerFlow 计划在未来版本中添加协作编辑功能：

- **多用户同时编辑**：支持多人同时编辑同一报告
- **变更追踪**：显示每个用户的编辑内容
- **评论功能**：在报告中添加和回复评论
- **权限控制**：设置不同用户的编辑权限

## 最佳实践

### 编辑技巧

1. **结构优先**：先调整报告的整体结构，再优化具体内容
2. **分段编辑**：一次专注于一个部分的编辑，避免大范围修改
3. **定期保存**：虽然有自动保存功能，但重要修改后手动保存更安全
4. **使用快捷键**：学习编辑器快捷键提高编辑效率
5. **适度使用 AI**：AI 辅助功能适合初步改进，但最终应由人工审核

### 常见快捷键

| 操作 | Windows/Linux | macOS |
|------|--------------|-------|
| 粗体 | Ctrl+B | Cmd+B |
| 斜体 | Ctrl+I | Cmd+I |
| 下划线 | Ctrl+U | Cmd+U |
| 标题 1 | Ctrl+Alt+1 | Cmd+Alt+1 |
| 标题 2 | Ctrl+Alt+2 | Cmd+Alt+2 |
| 标题 3 | Ctrl+Alt+3 | Cmd+Alt+3 |
| 有序列表 | Ctrl+Shift+7 | Cmd+Shift+7 |
| 无序列表 | Ctrl+Shift+8 | Cmd+Shift+8 |
| 代码块 | Ctrl+Alt+C | Cmd+Alt+C |
| 引用 | Ctrl+Shift+B | Cmd+Shift+B |
| 保存 | Ctrl+S | Cmd+S |
| 撤销 | Ctrl+Z | Cmd+Z |
| 重做 | Ctrl+Shift+Z | Cmd+Shift+Z |

## 故障排除

### 常见问题

1. **编辑器无响应**：
   - 尝试刷新页面
   - 检查浏览器控制台是否有错误信息
   - 确认浏览器是否支持所有功能（推荐使用 Chrome、Firefox 或 Edge 最新版）

2. **内容丢失**：
   - 检查版本历史，尝试恢复之前版本
   - 确认网络连接是否稳定
   - 下次编辑时更频繁地手动保存

3. **导出失败**：
   - 检查报告大小，过大的报告可能导致导出超时
   - 尝试分段导出或选择不同的导出格式
   - 确认服务器端导出服务是否正常运行

4. **AI 辅助功能失败**：
   - 确认选中的文本不要过长（建议不超过 2000 字）
   - 检查 LLM 服务是否可用
   - 尝试使用不同的 AI 辅助功能

### 联系支持

如果遇到无法解决的问题，请通过以下渠道获取支持：

- GitHub Issues：报告问题和提出功能请求
- GitHub Discussions：讨论和分享想法
- 官方网站：[deerflow.tech](https://deerflow.tech) 