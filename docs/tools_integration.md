# DeerFlow 工具集成设计

## 工具系统概述

DeerFlow 集成了多种工具，使代理能够执行各种任务，如网络搜索、内容爬取、代码执行和文本转语音等。工具系统设计遵循模块化原则，便于添加新工具和扩展现有功能。

## 核心工具集

### 1. 搜索工具

**功能**：执行网络搜索，获取与研究主题相关的信息。

**支持的搜索引擎**：
- **Tavily**：专为 AI 应用设计的搜索 API
- **DuckDuckGo**：注重隐私的搜索引擎
- **Brave Search**：具有高级功能的隐私搜索引擎
- **Arxiv**：科学论文搜索引擎

**实现**：
```python
def get_web_search_tool(max_results: int = 3):
    """获取配置的网络搜索工具。"""
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        return TavilySearchResults(max_results=max_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.DUCKDUCKGO.value:
        return DuckDuckGoSearchResults(num_results=max_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BRAVE_SEARCH.value:
        return BraveSearchResults(api_key=os.getenv("BRAVE_SEARCH_API_KEY"), max_results=max_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ARXIV.value:
        return ArxivQueryRun(top_k_results=max_results)
    else:
        raise ValueError(f"Unknown search engine: {SELECTED_SEARCH_ENGINE}")
```

**配置**：通过 `.env` 文件中的 `SEARCH_API` 变量配置。

### 2. 爬取工具

**功能**：爬取网页内容，提取结构化信息。

**特点**：
- 使用 Jina 进行内容爬取
- 支持 HTML 解析和内容提取
- 可处理各种网页格式

**实现**：
```python
@tool
def crawl_tool(url: str) -> str:
    """爬取指定 URL 的内容。"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 使用 BeautifulSoup 提取内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除脚本和样式元素
        for script in soup(["script", "style"]):
            script.extract()
            
        # 获取文本
        text = soup.get_text()
        
        # 处理文本，删除多余空白
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        return f"Error crawling {url}: {str(e)}"
```

### 3. Python REPL 工具

**功能**：执行 Python 代码，进行数据分析和处理。

**特点**：
- 支持交互式代码执行
- 可用于数据处理、分析和可视化
- 支持错误处理和状态保持

**实现**：
```python
class PythonREPLTool(BaseTool):
    """用于执行 Python 代码的工具。"""
    
    name = "python_repl"
    description = "一个 Python shell。使用此工具执行 Python 命令。输入应为有效的 Python 命令。如果你想查看变量的值，可以使用 print() 函数。"
    
    def _run(self, command: str) -> str:
        """执行 Python 代码。"""
        try:
            # 创建一个字典来存储本地变量
            local_vars = {}
            # 执行代码
            exec(command, globals(), local_vars)
            # 捕获标准输出
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(command, globals(), local_vars)
            return output.getvalue()
        except Exception as e:
            return f"Error: {str(e)}"

python_repl_tool = PythonREPLTool()
```

### 4. 文本转语音工具

**功能**：将文本转换为语音，生成高质量的音频文件。

**特点**：
- 使用 volcengine TTS API
- 支持速度、音量和音调调整
- 生成 MP3 格式音频

**实现**：
```python
class VolcengineTTS:
    """使用 volcengine TTS API 的文本转语音工具。"""
    
    def __init__(self):
        self.access_key = os.getenv("VOLCENGINE_ACCESS_KEY")
        self.secret_key = os.getenv("VOLCENGINE_SECRET_KEY")
        self.service_id = os.getenv("VOLCENGINE_SERVICE_ID")
        
    def synthesize_speech(
        self,
        text: str,
        speed_ratio: float = 1.0,
        volume_ratio: float = 1.0,
        pitch_ratio: float = 1.0
    ) -> bytes:
        """将文本转换为语音。"""
        # 实现 volcengine TTS API 调用
        # 返回音频数据
```

### 5. RAG 检索工具

**功能**：从知识库中检索相关信息。

**支持的 RAG 提供商**：
- **RAGFlow**：支持私有知识库检索

**实现**：
```python
def get_retriever_tool(resources: list[Resource] = None):
    """获取配置的检索工具。"""
    if RAG_PROVIDER == "ragflow":
        return RagFlowRetriever(
            api_url=os.getenv("RAGFLOW_API_URL"),
            api_key=os.getenv("RAGFLOW_API_KEY"),
            retrieval_size=int(os.getenv("RAGFLOW_RETRIEVAL_SIZE", "10")),
        )
    else:
        return None
```

## MCP 工具集成

DeerFlow 支持通过 Model Context Protocol (MCP) 集成外部工具和服务。

### MCP 服务配置

**配置示例**：
```python
mcp_settings = {
    "servers": {
        "mcp-github-trending": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-github-trending"],
            "enabled_tools": ["get_github_trending_repositories"],
            "add_to_agents": ["researcher"],
        }
    }
}
```

### MCP 客户端集成

**实现**：
```python
# 创建 MCP 客户端
mcp_client = MultiServerMCPClient(configurable.mcp_settings["servers"])

# 获取 MCP 工具
mcp_tools = mcp_client.get_tools_for_agent(agent_type)
```

## 工具装饰器

DeerFlow 使用装饰器模式增强工具功能：

### 日志装饰器

**功能**：记录工具调用和结果。

**实现**：
```python
def log_tool_use(func):
    """记录工具使用的装饰器。"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling tool {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"Tool {func.__name__} returned: {result[:100]}...")
        return result
    return wrapper
```

### 重试装饰器

**功能**：在工具调用失败时自动重试。

**实现**：
```python
def retry_on_failure(max_retries=3, delay=1):
    """失败时重试的装饰器。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise
                    logger.warning(f"Tool {func.__name__} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
        return wrapper
    return decorator
```

## 工具注册和发现

DeerFlow 使用工具注册机制，使代理能够发现和使用可用工具：

```python
def get_tools_for_agent(agent_type: str, config: RunnableConfig) -> list:
    """获取指定代理类型的工具列表。"""
    configurable = Configuration.from_runnable_config(config)
    
    # 获取默认工具
    default_tools = DEFAULT_TOOLS.get(agent_type, [])
    
    # 添加 MCP 工具（如果配置了）
    if configurable.mcp_settings and "servers" in configurable.mcp_settings:
        mcp_client = MultiServerMCPClient(configurable.mcp_settings["servers"])
        mcp_tools = mcp_client.get_tools_for_agent(agent_type)
        if mcp_tools:
            default_tools.extend(mcp_tools)
    
    return default_tools
```

## 工具配置系统

DeerFlow 使用集中式配置系统管理工具：

```python
# src/config/tools.py
DEFAULT_TOOLS = {
    "researcher": [
        get_web_search_tool,
        crawl_tool,
    ],
    "coder": [
        python_repl_tool,
    ],
    # 其他代理的默认工具...
}
```

## 扩展工具系统

### 添加新工具

要添加新工具，需要：

1. **创建工具实现**：
   ```python
   @tool
   def new_tool(param: str) -> str:
       """新工具的描述。"""
       # 工具实现
       return result
   ```

2. **注册工具**：
   ```python
   # 在 src/config/tools.py 中添加
   DEFAULT_TOOLS = {
       "researcher": [
           # 现有工具...
           new_tool,
       ],
   }
   ```

3. **更新导出**：
   ```python
   # 在 src/tools/__init__.py 中添加
   from .new_tool_module import new_tool
   
   __all__ = [
       # 现有工具...
       "new_tool",
   ]
   ```

### 集成外部服务

要集成外部服务，可以：

1. **创建 API 客户端**：
   ```python
   class ExternalServiceClient:
       def __init__(self, api_key: str):
           self.api_key = api_key
           
       def call_service(self, params: dict) -> dict:
           # 调用外部服务
           return result
   ```

2. **创建工具包装器**：
   ```python
   @tool
   def external_service_tool(query: str) -> str:
       """外部服务工具的描述。"""
       client = ExternalServiceClient(os.getenv("EXTERNAL_SERVICE_API_KEY"))
       result = client.call_service({"query": query})
       return json.dumps(result)
   ``` 