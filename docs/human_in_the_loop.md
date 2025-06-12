# DeerFlow 人机协作功能

## 概述

DeerFlow 的人机协作功能允许用户参与研究计划的制定和修改过程，结合人类专业知识与 AI 能力，创建更高质量、更符合需求的研究成果。本文档详细介绍 DeerFlow 的人机协作机制、工作流程和最佳实践。

## 人机协作机制

### 计划审查与反馈

DeerFlow 实现了一个交互式计划审查机制，允许用户在研究执行前审查自动生成的研究计划：

1. **计划生成**：系统自动分析用户查询，生成初步研究计划
2. **计划呈现**：向用户展示研究计划，包括研究步骤和预期结果
3. **用户反馈**：用户可以接受计划或提供修改建议
4. **计划调整**：系统根据用户反馈调整研究计划
5. **计划执行**：最终确认的计划被执行

### 反馈格式

用户可以通过以下格式提供反馈：

1. **接受计划**：回复 `[ACCEPTED]` 表示接受当前计划
2. **修改计划**：回复 `[EDIT_PLAN] 修改建议` 提供具体修改建议

例如：
```
[EDIT_PLAN] 请增加一个关于市场竞争分析的步骤，并减少技术细节的研究深度
```

### 自动接受选项

为了提高效率，DeerFlow 支持自动接受研究计划：

1. **通过 API**：设置 `auto_accepted_plan: true` 参数
2. **通过 Web 界面**：在设置中启用"自动接受计划"选项
3. **通过命令行**：使用 `--auto-accept` 参数

## 技术实现

### 人机反馈节点

DeerFlow 通过 `human_feedback_node` 实现人机协作功能：

```python
def human_feedback_node(
    state,
) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    current_plan = state.get("current_plan", "")
    # 检查计划是否自动接受
    auto_accepted_plan = state.get("auto_accepted_plan", False)
    if not auto_accepted_plan:
        feedback = interrupt("请审查研究计划。")

        # 如果反馈不是接受，返回规划器节点
        if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
            return Command(
                update={
                    "messages": [
                        HumanMessage(content=feedback, name="feedback"),
                    ],
                },
                goto="planner",
            )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
            logger.info("计划被用户接受。")
        else:
            raise TypeError(f"中断值 {feedback} 不受支持。")

    # 如果计划被接受，运行后续节点
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    goto = "research_team"
    try:
        current_plan = repair_json_output(current_plan)
        # 增加计划迭代次数
        plan_iterations += 1
        # 解析计划
        new_plan = json.loads(current_plan)
        if new_plan["has_enough_context"]:
            goto = "reporter"
    except json.JSONDecodeError:
        logger.warning("规划器响应不是有效的 JSON")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")

    return Command(
        update={
            "current_plan": Plan.model_validate(new_plan),
            "plan_iterations": plan_iterations,
            "locale": new_plan["locale"],
        },
        goto=goto,
    )
```

### 中断机制

DeerFlow 使用 LangGraph 的中断机制实现用户反馈：

```python
feedback = interrupt("请审查研究计划。")
```

这会暂停工作流，等待用户输入，然后将用户输入作为 `feedback` 返回。

## Web 界面集成

### 计划审查面板

Web 界面中的计划审查面板提供直观的计划审查体验：

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

### 设置选项

Web 界面的设置面板允许用户配置人机协作行为：

```tsx
export function SettingsPanel() {
  const settings = useStore((state) => state.settings);
  const updateSettings = useStore((state) => state.updateSettings);
  
  return (
    <div className="settings-panel">
      <h3>研究设置</h3>
      <div className="setting-item">
        <label>
          <input
            type="checkbox"
            checked={settings.autoAcceptedPlan}
            onChange={(e) => updateSettings({ autoAcceptedPlan: e.target.checked })}
          />
          自动接受研究计划
        </label>
      </div>
      <div className="setting-item">
        <label>
          最大计划迭代次数
          <input
            type="number"
            value={settings.maxPlanIterations}
            onChange={(e) => updateSettings({ maxPlanIterations: parseInt(e.target.value) })}
            min="1"
            max="5"
          />
        </label>
      </div>
      <div className="setting-item">
        <label>
          最大研究步骤数
          <input
            type="number"
            value={settings.maxStepNum}
            onChange={(e) => updateSettings({ maxStepNum: parseInt(e.target.value) })}
            min="1"
            max="10"
          />
        </label>
      </div>
    </div>
  );
}
```

## API 集成

### 请求参数

通过 API 使用人机协作功能时，可以设置以下参数：

```json
{
  "messages": [{ "role": "user", "content": "分析比特币价格波动的原因" }],
  "thread_id": "my_thread_id",
  "auto_accepted_plan": false,
  "feedback": null
}
```

当需要提供反馈时，可以发送：

```json
{
  "messages": [{ "role": "user", "content": "分析比特币价格波动的原因" }],
  "thread_id": "my_thread_id",
  "feedback": "[EDIT_PLAN] 请增加关于监管影响的分析"
}
```

### 响应格式

API 响应包含当前计划和消息历史：

```json
{
  "messages": [
    { "role": "user", "content": "分析比特币价格波动的原因" },
    { "role": "assistant", "content": "...", "name": "coordinator" },
    { "role": "assistant", "content": "...", "name": "planner" }
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

## 命令行使用

在命令行中使用人机协作功能：

```bash
# 默认模式（需要人工审查计划）
uv run main.py "分析比特币价格波动的原因"

# 自动接受计划模式
uv run main.py --auto-accept "分析比特币价格波动的原因"

# 设置最大计划迭代次数
uv run main.py --max-plan-iterations 3 "分析比特币价格波动的原因"

# 设置最大步骤数
uv run main.py --max-step-num 5 "分析比特币价格波动的原因"
```

## 最佳实践

### 有效反馈指南

为了获得最佳结果，请遵循以下反馈指南：

1. **具体明确**：提供具体的修改建议，而非模糊的指示
2. **重点突出**：关注研究计划的结构和内容，而非细节表述
3. **合理范围**：考虑系统能力范围，避免过于复杂的要求
4. **平衡深度**：在研究深度和广度之间找到平衡

### 反馈示例

#### 有效反馈示例：

```
[EDIT_PLAN] 请增加一个关于监管政策影响的步骤，并将市场情绪分析的优先级提高
```

```
[EDIT_PLAN] 减少技术分析的深度，增加宏观经济因素的分析，特别是通货膨胀对比特币价格的影响
```

#### 无效反馈示例：

```
[EDIT_PLAN] 让计划更好一点
```

```
[EDIT_PLAN] 完全重写计划，使用完全不同的方法
```

### 自动接受场景

以下场景适合使用自动接受功能：

1. **批量处理**：需要处理大量研究请求
2. **标准研究**：进行标准化、常规的研究任务
3. **时间敏感**：需要快速获取研究结果
4. **初步探索**：进行初步探索，后续再进行深入研究

### 人工审查场景

以下场景建议进行人工审查：

1. **复杂研究**：涉及复杂、多维度的研究主题
2. **专业领域**：研究特定专业领域，需要专业知识指导
3. **定制需求**：有特定的研究方向或方法要求
4. **高质量要求**：对研究质量有较高要求

## 高级功能

### 多轮计划迭代

DeerFlow 支持多轮计划迭代，允许逐步完善研究计划：

1. 设置 `max_plan_iterations` 参数大于 1
2. 系统会在每次收到用户反馈后生成新的计划
3. 用户可以继续提供反馈，直到满意或达到最大迭代次数

### 计划执行监控

DeerFlow 允许用户监控计划执行进度：

1. Web 界面实时显示当前执行的研究步骤
2. 每个步骤完成后显示中间结果
3. 用户可以查看整个研究过程的详细日志

### 计划执行干预

在未来版本中，DeerFlow 计划支持研究执行过程中的干预：

1. 暂停正在执行的研究
2. 修改后续研究步骤
3. 基于中间结果调整研究方向

## 故障排除

### 常见问题

1. **反馈未被接受**：
   - 确保反馈格式正确（以 `[EDIT_PLAN]` 或 `[ACCEPTED]` 开头）
   - 检查反馈内容是否过长或包含特殊字符

2. **计划修改不符合预期**：
   - 提供更具体、更明确的修改建议
   - 尝试分步骤提供多次反馈

3. **系统未等待反馈**：
   - 检查 `auto_accepted_plan` 设置是否为 `true`
   - 验证系统配置是否正确

### 联系支持

如果遇到无法解决的问题，请通过以下渠道获取支持：

- GitHub Issues：报告问题和提出功能请求
- GitHub Discussions：讨论和分享想法
- 官方网站：[deerflow.tech](https://deerflow.tech) 