# DeerFlow API 参考文档

## API 概述

DeerFlow 提供了一组 RESTful API，允许开发者以编程方式访问和控制 DeerFlow 的深度研究功能。API 支持研究查询提交、状态查询、结果获取等操作，使 DeerFlow 能够轻松集成到各种应用程序中。

## 基本信息

- **基础 URL**: `http://localhost:8000/api`（本地部署）或您的自定义部署 URL
- **内容类型**: 所有请求和响应均使用 `application/json`
- **认证**: 目前不需要 API 密钥，但可能在未来版本中添加

## API 端点

### 1. 聊天 API

#### 发送消息

**请求**:

```
POST /chat
```

**请求体**:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "分析比特币价格波动的原因"
    }
  ],
  "thread_id": "my_thread_id",
  "auto_accepted_plan": true,
  "feedback": null
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| messages | array | 是 | 消息数组，包含角色和内容 |
| thread_id | string | 否 | 会话线程 ID，用于关联多个消息（默认为 "default"） |
| auto_accepted_plan | boolean | 否 | 是否自动接受研究计划（默认为 false） |
| feedback | string | 否 | 对研究计划的反馈，格式为 "[EDIT_PLAN] 反馈内容" 或 "[ACCEPTED]" |

**响应**:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "分析比特币价格波动的原因"
    },
    {
      "role": "assistant",
      "content": "我将为您分析比特币价格波动的原因...",
      "name": "coordinator"
    },
    {
      "role": "assistant",
      "content": "...",
      "name": "planner"
    }
  ],
  "current_plan": {
    "locale": "zh-CN",
    "has_enough_context": false,
    "thought": "...",
    "title": "比特币价格波动分析",
    "steps": [...]
  }
}
```

#### 流式消息

**请求**:

```
POST /chat/stream
```

**请求体**: 与 `/chat` 相同

**响应**: 

服务器发送事件 (SSE) 流，每个事件格式如下:

```
data: {"messages": [...], "current_plan": {...}}
```

### 2. 文本转语音 API

**请求**:

```
POST /tts
```

**请求体**:

```json
{
  "text": "这是要转换为语音的文本内容",
  "speed_ratio": 1.0,
  "volume_ratio": 1.0,
  "pitch_ratio": 1.0
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| text | string | 是 | 要转换为语音的文本 |
| speed_ratio | float | 否 | 语速比例，范围 0.5-2.0（默认为 1.0） |
| volume_ratio | float | 否 | 音量比例，范围 0.5-2.0（默认为 1.0） |
| pitch_ratio | float | 否 | 音调比例，范围 0.5-2.0（默认为 1.0） |

**响应**:

二进制音频数据 (MP3 格式)

### 3. 演示文稿生成 API

**请求**:

```
POST /ppt
```

**请求体**:

```json
{
  "content": "要转换为演示文稿的内容",
  "template": "default"
}
```

**参数说明**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| content | string | 是 | 要转换为演示文稿的内容 |
| template | string | 否 | 演示文稿模板名称（默认为 "default"） |

**响应**:

二进制演示文稿数据 (PPTX 格式)

### 4. 研究状态 API

**请求**:

```
GET /research/{thread_id}/status
```

**参数说明**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| thread_id | string | 是 | 研究线程 ID |

**响应**:

```json
{
  "status": "completed",
  "progress": 100,
  "current_step": "报告生成",
  "steps_completed": 3,
  "total_steps": 3
}
```

### 5. 研究结果 API

**请求**:

```
GET /research/{thread_id}/result
```

**参数说明**:

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| thread_id | string | 是 | 研究线程 ID |

**响应**:

```json
{
  "title": "比特币价格波动分析",
  "content": "# 比特币价格波动分析\n\n## 引言\n\n...",
  "sections": [
    {
      "title": "引言",
      "content": "..."
    },
    {
      "title": "市场因素",
      "content": "..."
    }
  ],
  "metadata": {
    "created_at": "2023-09-15T14:30:00Z",
    "updated_at": "2023-09-15T14:35:00Z",
    "word_count": 1500
  }
}
```

## 错误处理

API 使用标准 HTTP 状态码表示请求状态：

- **200 OK**: 请求成功
- **400 Bad Request**: 请求参数错误
- **404 Not Found**: 资源不存在
- **500 Internal Server Error**: 服务器错误

错误响应格式：

```json
{
  "error": {
    "code": "invalid_request",
    "message": "缺少必需的参数: messages"
  }
}
```

## 服务器实现

DeerFlow API 服务器使用 FastAPI 实现，位于 `src/server/` 目录中。主要组件包括：

### 1. 应用初始化

```python
# src/server/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DeerFlow API",
    description="DeerFlow 深度研究框架 API",
    version="0.1.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 聊天路由

```python
# src/server/routes/chat.py
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from src.graph import build_graph

router = APIRouter()

@router.post("/chat")
async def chat(request: dict):
    # 处理聊天请求
    # 返回响应
    
@router.post("/chat/stream")
async def chat_stream(request: dict):
    # 处理流式聊天请求
    # 返回 SSE 流
```

### 3. 文本转语音路由

```python
# src/server/routes/tts.py
from fastapi import APIRouter
from fastapi.responses import Response
from src.tools import VolcengineTTS

router = APIRouter()

@router.post("/tts")
async def text_to_speech(request: dict):
    # 处理文本转语音请求
    # 返回音频数据
```

## 客户端示例

### JavaScript/TypeScript

```typescript
// 发送聊天请求
async function sendChatRequest(message: string) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: [{ role: 'user', content: message }],
      thread_id: 'example_thread',
      auto_accepted_plan: true,
    }),
  });
  
  return await response.json();
}

// 使用流式 API
async function streamChatRequest(message: string, onChunk: (chunk: any) => void) {
  const response = await fetch('http://localhost:8000/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: [{ role: 'user', content: message }],
      thread_id: 'example_thread',
      auto_accepted_plan: true,
    }),
  });
  
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        
        try {
          const parsedData = JSON.parse(data);
          onChunk(parsedData);
        } catch (e) {
          console.error('Error parsing chunk:', e);
        }
      }
    }
  }
}
```

### Python

```python
import requests
import json

# 发送聊天请求
def send_chat_request(message):
    response = requests.post(
        'http://localhost:8000/api/chat',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'messages': [{'role': 'user', 'content': message}],
            'thread_id': 'example_thread',
            'auto_accepted_plan': True,
        })
    )
    return response.json()

# 生成 TTS 音频
def generate_tts(text):
    response = requests.post(
        'http://localhost:8000/api/tts',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'text': text,
            'speed_ratio': 1.0,
            'volume_ratio': 1.0,
            'pitch_ratio': 1.0,
        })
    )
    
    with open('output.mp3', 'wb') as f:
        f.write(response.content)
    
    return 'output.mp3'
```

## 限制和注意事项

1. **请求大小限制**：文本内容不应超过模型的最大上下文窗口大小
2. **速率限制**：API 可能实施速率限制以防止过度使用
3. **并发请求**：服务器可能限制每个客户端的并发请求数
4. **长时间运行的请求**：研究查询可能需要较长时间处理，建议使用流式 API
5. **数据持久性**：研究结果可能有时间限制，建议客户端保存重要结果 