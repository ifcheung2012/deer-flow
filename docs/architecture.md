# DeerFlow 架构设计

## 整体架构

DeerFlow 采用基于 LangGraph 的模块化多代理系统架构，通过定义明确的消息传递系统实现组件间通信。系统架构如下图所示：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  协调器     │────▶│  规划器     │────▶│  人类反馈   │
│ Coordinator │     │  Planner    │     │  Feedback   │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
       │                  ▲                    │
       │                  │                    │
       ▼                  │                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│ 背景调查    │────▶│  研究团队   │────▶│  报告生成   │
│ Background  │     │  Research   │     │  Reporter   │
│             │     │   Team      │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          │
                    ┌─────┴─────┐
                    │           │
            ┌───────▼─┐   ┌─────▼───┐
            │         │   │         │
            │ 研究员  │   │ 编码员  │
            │Researcher│   │ Coder   │
            │         │   │         │
            └─────────┘   └─────────┘
```

## 核心组件

### 1. 协调器 (Coordinator)

**职责**：
- 作为工作流的入口点，管理整个研究生命周期
- 基于用户输入启动研究流程
- 适时将任务委派给规划器
- 充当用户和系统之间的主要接口

**实现**：
- 位于 `src/graph/nodes.py` 中的 `coordinator_node` 函数
- 解析用户查询并确定下一步行动
- 决定是否需要进行背景调查

### 2. 规划器 (Planner)

**职责**：
- 分析研究目标并创建结构化执行计划
- 确定是否有足够的上下文或是否需要更多研究
- 管理研究流程并决定何时生成最终报告

**实现**：
- 位于 `src/graph/nodes.py` 中的 `planner_node` 函数
- 使用 `src/prompts/planner.md` 中的提示模板
- 生成 `Plan` 对象，定义在 `src/prompts/planner_model.py` 中

### 3. 研究团队 (Research Team)

**职责**：
- 执行规划器制定的计划
- 收集和处理研究所需的信息
- 协调不同专业代理的工作

**组成**：
- **研究员 (Researcher)**：使用网络搜索、爬取等工具收集信息
- **编码员 (Coder)**：使用 Python REPL 工具执行代码分析和技术任务

**实现**：
- 位于 `src/graph/nodes.py` 中的 `research_team_node`、`researcher_node` 和 `coder_node` 函数
- 使用 `src/agents/agents.py` 中的代理创建机制
- 利用 `src/tools` 目录下的各种工具

### 4. 报告生成器 (Reporter)

**职责**：
- 聚合研究团队的发现
- 处理和结构化收集的信息
- 生成全面的研究报告

**实现**：
- 位于 `src/graph/nodes.py` 中的 `reporter_node` 函数
- 使用 `src/prompts/reporter.md` 中的提示模板

## 状态管理

DeerFlow 使用 LangGraph 的状态图来管理工作流程：

- **状态定义**：在 `src/graph/types.py` 中定义了 `State` 类型
- **图构建**：在 `src/graph/builder.py` 中通过 `build_graph` 函数构建状态图
- **边缘条件**：定义了条件边缘，如 `continue_to_running_research_team` 函数

## 工具集成

DeerFlow 集成了多种工具以支持研究流程：

1. **搜索工具**：
   - 支持多种搜索引擎：Tavily、DuckDuckGo、Brave Search、Arxiv
   - 实现在 `src/tools/search.py` 中

2. **爬取工具**：
   - 网页内容爬取和提取
   - 实现在 `src/tools/crawl.py` 中

3. **Python REPL**：
   - 执行 Python 代码进行数据分析
   - 实现在 `src/tools/python_repl.py` 中

4. **文本转语音**：
   - 使用 volcengine TTS API 生成高质量音频
   - 实现在 `src/tools/tts.py` 中

5. **MCP 集成**：
   - 支持 Model Context Protocol 服务
   - 通过 `MultiServerMCPClient` 实现

## 用户界面

DeerFlow 提供两种用户界面：

1. **控制台界面**：
   - 通过 `main.py` 提供简单的命令行交互
   - 支持交互式模式和直接查询模式

2. **Web 界面**：
   - 基于 Next.js 构建的现代 Web 应用
   - 位于 `web` 目录下
   - 提供更动态和引人入胜的交互体验
   - 支持报告后编辑和 AI 辅助润色

## 配置系统

DeerFlow 使用灵活的配置系统：

- **配置加载**：通过 `src/config/loader.py` 加载 YAML 配置
- **环境变量**：通过 `.env` 文件配置 API 密钥和服务选择
- **运行时配置**：通过 `src/config/configuration.py` 中的 `Configuration` 类管理

## 扩展性设计

DeerFlow 的扩展性设计体现在：

1. **模块化架构**：各组件职责明确，易于替换和扩展
2. **工具抽象**：统一的工具接口，便于添加新工具
3. **提示模板**：独立的提示模板文件，易于定制和优化
4. **LLM 抽象**：支持多种 LLM 模型，通过配置文件切换
5. **MCP 集成**：支持动态加载外部工具和服务 