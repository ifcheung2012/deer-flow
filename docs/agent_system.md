# DeerFlow 代理系统设计

## 代理系统概述

DeerFlow 采用多代理协作系统架构，通过不同专业代理的协作完成复杂的研究任务。代理系统基于 LangGraph 框架构建，使用状态图管理代理间的交互和工作流程。

## 代理类型及职责

### 1. 协调器代理 (Coordinator Agent)

**职责**：
- 作为系统的入口点，接收和解析用户查询
- 决定是否需要进行背景调查
- 将任务委派给适当的代理
- 管理整个研究流程的生命周期

**工作流程**：
1. 接收用户输入
2. 分析查询内容
3. 决定是否需要背景调查
4. 将任务委派给规划器或直接结束流程

**实现**：
```python
def coordinator_node(state: State, config: RunnableConfig) -> Command[Literal["planner", "background_investigator", "__end__"]]:
    # 解析用户查询
    # 决定下一步行动
    # 返回适当的命令
```

### 2. 规划器代理 (Planner Agent)

**职责**：
- 分析研究目标
- 创建结构化的研究计划
- 确定是否有足够的上下文或需要更多研究
- 管理研究流程并决定何时生成最终报告

**工作流程**：
1. 接收研究主题
2. 分析主题并确定研究范围
3. 将研究任务分解为具体步骤
4. 创建结构化的研究计划
5. 确定是否需要人类反馈

**实现**：
```python
def planner_node(state: State, config: RunnableConfig) -> Command[Literal["human_feedback", "reporter"]]:
    # 生成研究计划
    # 决定是否有足够上下文
    # 返回适当的命令
```

### 3. 研究员代理 (Researcher Agent)

**职责**：
- 执行网络搜索和信息收集
- 使用各种工具（如搜索引擎、爬虫）获取信息
- 整合和筛选收集的信息
- 将结果提供给研究团队

**工具集**：
- 网络搜索工具
- 网页爬取工具
- MCP 服务工具

**实现**：
```python
async def researcher_node(state: State, config: RunnableConfig) -> Command[Literal["research_team"]]:
    # 设置研究员代理
    # 执行研究步骤
    # 返回结果
```

### 4. 编码员代理 (Coder Agent)

**职责**：
- 执行代码分析和技术任务
- 使用 Python REPL 工具进行数据处理
- 执行复杂计算和数据分析
- 将结果提供给研究团队

**工具集**：
- Python REPL 工具
- 数据处理工具
- 代码执行环境

**实现**：
```python
async def coder_node(state: State, config: RunnableConfig) -> Command[Literal["research_team"]]:
    # 设置编码员代理
    # 执行编码步骤
    # 返回结果
```

### 5. 报告生成器代理 (Reporter Agent)

**职责**：
- 聚合研究团队的发现
- 处理和结构化收集的信息
- 生成全面的研究报告
- 格式化输出结果

**工作流程**：
1. 接收研究结果
2. 分析和整合信息
3. 生成结构化报告
4. 格式化最终输出

**实现**：
```python
def reporter_node(state: State, config: RunnableConfig):
    # 聚合研究结果
    # 生成最终报告
    # 返回格式化输出
```

## 代理创建机制

DeerFlow 使用工厂模式创建代理，确保一致的配置和行为：

```python
def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str):
    """工厂函数，创建具有一致配置的代理。"""
    return create_react_agent(
        name=agent_name,
        model=get_llm_by_type(AGENT_LLM_MAP[agent_type]),
        tools=tools,
        prompt=lambda state: apply_prompt_template(prompt_template, state),
    )
```

## 代理间通信

代理间通信通过 LangGraph 的状态管理机制实现：

1. **状态共享**：代理通过共享状态对象传递信息
2. **命令模式**：代理通过返回命令对象控制工作流程
3. **消息传递**：代理可以向状态添加消息，供其他代理使用

示例：
```python
return Command(
    update={
        "messages": [AIMessage(content=full_response, name="planner")],
        "current_plan": new_plan,
    },
    goto="reporter",
)
```

## 人类反馈集成

DeerFlow 支持人类参与研究计划的制定和修改：

1. **计划审查**：当启用人类反馈时，系统会在执行前呈现生成的研究计划
2. **提供反馈**：人类可以接受计划或提供修改建议
3. **自动接受**：可以配置自动接受计划，跳过审查过程

**实现**：
```python
def human_feedback_node(state) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    # 检查计划是否自动接受
    # 如果不是，中断并等待人类反馈
    # 处理反馈并决定下一步
```

## 代理配置系统

DeerFlow 使用灵活的配置系统为不同代理分配适当的 LLM 模型：

```python
# src/config/agents.py
AGENT_LLM_MAP = {
    "coordinator": "basic",
    "planner": "basic",
    "researcher": "basic",
    "coder": "basic",
    "reporter": "basic",
}
```

这允许为不同的代理角色分配不同的模型，优化性能和成本。

## 代理提示工程

每个代理使用专门设计的提示模板，定义在单独的 Markdown 文件中：

1. **协调器提示**：`src/prompts/coordinator.md`
2. **规划器提示**：`src/prompts/planner.md`
3. **研究员提示**：`src/prompts/researcher.md`
4. **编码员提示**：`src/prompts/coder.md`
5. **报告生成器提示**：`src/prompts/reporter.md`

提示应用通过 `apply_prompt_template` 函数实现，支持动态插入状态信息。

## 扩展性设计

DeerFlow 的代理系统设计支持多种扩展方式：

1. **添加新代理**：可以通过实现新的节点函数和提示模板添加新代理
2. **扩展工具集**：可以为现有代理添加新工具，增强其能力
3. **自定义提示**：可以修改提示模板，调整代理行为
4. **集成外部服务**：通过 MCP 集成支持外部工具和服务 