# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.agents import create_agent
from src.tools.search import LoggedTavilySearch
from src.tools import (
    crawl_tool,
    get_web_search_tool,
    get_retriever_tool,
    python_repl_tool,
)

from src.config.agents import AGENT_LLM_MAP
from src.config.configuration import Configuration
from src.llms.llm import get_llm_by_type
from src.prompts.planner_model import Plan
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output

from .types import State
from ..config import SELECTED_SEARCH_ENGINE, SearchEngine

logger = logging.getLogger(__name__)  # 获取日志记录器


@tool
def handoff_to_planner(
    research_topic: Annotated[str, "The topic of the research task to be handed off."],  # 要移交的研究任务主题
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],  # 用户检测到的语言区域设置
):
    """
    移交给规划代理来制定计划
    
    这个工具不返回任何内容：我们只是将其用作LLM表示需要移交给规划代理的方式
    
    参数:
        research_topic: 要移交的研究任务主题
        locale: 用户检测到的语言区域设置
    """
    # 移交给规划代理来制定计划
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    # 此工具不返回任何内容：我们只是将其用作LLM表示需要移交给规划代理的方式
    return


def background_investigation_node(state: State, config: RunnableConfig):
    """
    背景调查节点，用于在规划前收集相关信息
    
    参数:
        state: 当前状态
        config: 可运行配置
        
    返回:
        包含背景调查结果的字典
    """
    logger.info("background investigation node is running.")  # 背景调查节点正在运行
    configurable = Configuration.from_runnable_config(config)  # 从可运行配置创建配置
    query = state.get("research_topic")  # 获取研究主题
    background_investigation_results = None  # 背景调查结果
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        searched_content = LoggedTavilySearch(
            max_results=configurable.max_search_results  # 最大搜索结果数
        ).invoke(query)  # 调用Tavily搜索
        if isinstance(searched_content, list):
            background_investigation_results = [
                f"## {elem['title']}\n\n{elem['content']}" for elem in searched_content
            ]  # 格式化搜索结果
            return {
                "background_investigation_results": "\n\n".join(
                    background_investigation_results  # 将结果连接成字符串
                )
            }
        else:
            logger.error(
                f"Tavily search returned malformed response: {searched_content}"  # Tavily搜索返回格式错误的响应
            )
    else:
        background_investigation_results = get_web_search_tool(
            configurable.max_search_results  # 最大搜索结果数
        ).invoke(query)  # 调用网络搜索工具
    return {
        "background_investigation_results": json.dumps(
            background_investigation_results, ensure_ascii=False  # 确保非ASCII字符不被转义
        )
    }


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter"]]:
    """
    规划节点，生成完整计划
    
    参数:
        state: 当前状态
        config: 可运行配置
        
    返回:
        命令，指示下一步是人类反馈还是报告员
    """
    logger.info("Planner generating full plan")  # 规划员正在生成完整计划
    configurable = Configuration.from_runnable_config(config)  # 从可运行配置创建配置
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0  # 获取计划迭代次数
    messages = apply_prompt_template("planner", state, configurable)  # 应用规划员提示模板

    if state.get("enable_background_investigation") and state.get(
        "background_investigation_results"  # 如果启用背景调查且有背景调查结果
    ):
        messages += [
            {
                "role": "user",
                "content": (
                    "background investigation results of user query:\n"  # 用户查询的背景调查结果
                    + state["background_investigation_results"]
                    + "\n"
                ),
            }
        ]  # 添加背景调查结果消息

    if AGENT_LLM_MAP["planner"] == "basic":
        llm = get_llm_by_type(AGENT_LLM_MAP["planner"]).with_structured_output(
            Plan,
            method="json_mode",  # 使用JSON模式输出结构化数据
        )  # 获取基本规划员LLM
    else:
        llm = get_llm_by_type(AGENT_LLM_MAP["planner"])  # 获取规划员LLM

    # if the plan iterations is greater than the max plan iterations, return the reporter node
    # 如果计划迭代次数大于最大计划迭代次数，返回报告员节点
    if plan_iterations >= configurable.max_plan_iterations:
        return Command(goto="reporter")  # 返回报告员命令

    full_response = ""  # 完整响应
    if AGENT_LLM_MAP["planner"] == "basic":
        response = llm.invoke(messages)  # 调用LLM
        full_response = response.model_dump_json(indent=4, exclude_none=True)  # 将响应转换为JSON字符串
    else:
        response = llm.stream(messages)  # 流式调用LLM
        for chunk in response:
            full_response += chunk.content  # 累加响应内容
    logger.debug(f"Current state messages: {state['messages']}")  # 记录当前状态消息
    logger.info(f"Planner response: {full_response}")  # 记录规划员响应

    try:
        curr_plan = json.loads(repair_json_output(full_response))  # 修复并解析JSON输出
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")  # 规划员响应不是有效的JSON
        if plan_iterations > 0:
            return Command(goto="reporter")  # 如果已经有计划迭代，返回报告员命令
        else:
            return Command(goto="__end__")  # 否则结束
    if curr_plan.get("has_enough_context"):
        logger.info("Planner response has enough context.")  # 规划员响应有足够的上下文
        new_plan = Plan.model_validate(curr_plan)  # 验证计划模型
        return Command(
            update={
                "messages": [AIMessage(content=full_response, name="planner")],  # 更新消息
                "current_plan": new_plan,  # 更新当前计划
            },
            goto="reporter",  # 前往报告员
        )
    return Command(
        update={
            "messages": [AIMessage(content=full_response, name="planner")],  # 更新消息
            "current_plan": full_response,  # 更新当前计划为完整响应
        },
        goto="human_feedback",  # 前往人类反馈
    )


def human_feedback_node(
    state,
) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    """
    人类反馈节点，处理用户对计划的反馈
    
    参数:
        state: 当前状态
        
    返回:
        命令，指示下一步是规划员、研究团队、报告员还是结束
    """
    current_plan = state.get("current_plan", "")  # 获取当前计划
    # check if the plan is auto accepted
    # 检查计划是否自动接受
    auto_accepted_plan = state.get("auto_accepted_plan", False)  # 获取是否自动接受计划
    if not auto_accepted_plan:
        feedback = interrupt("Please Review the Plan.")  # 中断，请求用户审查计划

        # if the feedback is not accepted, return the planner node
        # 如果反馈不被接受，返回规划员节点
        if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):  # 如果反馈是编辑计划
            return Command(
                update={
                    "messages": [
                        HumanMessage(content=feedback, name="feedback"),  # 更新消息
                    ],
                },
                goto="planner",  # 前往规划员
            )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):  # 如果反馈是接受
            logger.info("Plan is accepted by user.")  # 计划被用户接受
        else:
            raise TypeError(f"Interrupt value of {feedback} is not supported.")  # 不支持的中断值

    # if the plan is accepted, run the following node
    # 如果计划被接受，运行以下节点
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0  # 获取计划迭代次数
    goto = "research_team"  # 默认前往研究团队
    try:
        current_plan = repair_json_output(current_plan)  # 修复JSON输出
        # increment the plan iterations
        # 增加计划迭代次数
        plan_iterations += 1  # 计划迭代次数加1
        # parse the plan
        # 解析计划
        new_plan = json.loads(current_plan)  # 解析JSON
        if new_plan["has_enough_context"]:  # 如果有足够的上下文
            goto = "reporter"  # 前往报告员
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")  # 规划员响应不是有效的JSON
        if plan_iterations > 0:
            return Command(goto="reporter")  # 如果已经有计划迭代，返回报告员命令
        else:
            return Command(goto="__end__")  # 否则结束

    return Command(
        update={
            "current_plan": Plan.model_validate(new_plan),  # 验证并更新当前计划
            "plan_iterations": plan_iterations,  # 更新计划迭代次数
            "locale": new_plan["locale"],  # 更新区域设置
        },
        goto=goto,  # 前往下一个节点
    )


def coordinator_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner", "background_investigator", "__end__"]]:
    """
    协调员节点，与客户沟通
    
    参数:
        state: 当前状态
        config: 可运行配置
        
    返回:
        命令，指示下一步是规划员、背景调查员还是结束
    """
    logger.info("Coordinator talking.")  # 协调员正在交谈
    configurable = Configuration.from_runnable_config(config)  # 从可运行配置创建配置
    messages = apply_prompt_template("coordinator", state)  # 应用协调员提示模板
    response = (
        get_llm_by_type(AGENT_LLM_MAP["coordinator"])  # 获取协调员LLM
        .bind_tools([handoff_to_planner])  # 绑定移交给规划员工具
        .invoke(messages)  # 调用LLM
    )
    logger.debug(f"Current state messages: {state['messages']}")  # 记录当前状态消息

    goto = "__end__"  # 默认前往结束
    locale = state.get("locale", "en-US")  # Default locale if not specified  # 默认区域设置（如果未指定）
    research_topic = state.get("research_topic", "")  # 获取研究主题

    if len(response.tool_calls) > 0:  # 如果有工具调用
        goto = "planner"  # 前往规划员
        if state.get("enable_background_investigation"):  # 如果启用背景调查
            # if the search_before_planning is True, add the web search tool to the planner agent
            # 如果在规划前搜索为True，将网络搜索工具添加到规划员代理
            goto = "background_investigator"  # 前往背景调查员
        try:
            for tool_call in response.tool_calls:  # 遍历工具调用
                if tool_call.get("name", "") != "handoff_to_planner":  # 如果不是移交给规划员工具
                    continue
                if tool_call.get("args", {}).get("locale") and tool_call.get(
                    "args", {}
                ).get("research_topic"):  # 如果有区域设置和研究主题
                    locale = tool_call.get("args", {}).get("locale")  # 获取区域设置
                    research_topic = tool_call.get("args", {}).get("research_topic")  # 获取研究主题
                    break
        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")  # 记录处理工具调用错误
    else:
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."  # 协调员响应不包含工具调用，终止工作流执行
        )
        logger.debug(f"Coordinator response: {response}")  # 记录协调员响应

    return Command(
        update={
            "locale": locale,  # 更新区域设置
            "research_topic": research_topic,  # 更新研究主题
            "resources": configurable.resources,  # 更新资源
        },
        goto=goto,  # 前往下一个节点
    )


def reporter_node(state: State, config: RunnableConfig):
    """
    报告员节点，编写最终报告
    
    参数:
        state: 当前状态
        config: 可运行配置
        
    返回:
        包含最终报告的字典
    """
    logger.info("Reporter write final report")  # 报告员编写最终报告
    configurable = Configuration.from_runnable_config(config)  # 从可运行配置创建配置
    current_plan = state.get("current_plan")  # 获取当前计划
    input_ = {
        "messages": [
            HumanMessage(
                f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"  # 研究需求、任务和描述
            )
        ],
        "locale": state.get("locale", "en-US"),  # 区域设置
    }
    invoke_messages = apply_prompt_template("reporter", input_, configurable)  # 应用报告员提示模板
    observations = state.get("observations", [])  # 获取观察结果

    # Add a reminder about the new report format, citation style, and table usage
    # 添加关于新报告格式、引用样式和表格使用的提醒
    invoke_messages.append(
        HumanMessage(
            content="IMPORTANT: Structure your report according to the format in the prompt. Remember to include:\n\n1. Key Points - A bulleted list of the most important findings\n2. Overview - A brief introduction to the topic\n3. Detailed Analysis - Organized into logical sections\n4. Survey Note (optional) - For more comprehensive reports\n5. Key Citations - List all references at the end\n\nFor citations, DO NOT include inline citations in the text. Instead, place all citations in the 'Key Citations' section at the end using the format: `- [Source Title](URL)`. Include an empty line between each citation for better readability.\n\nPRIORITIZE USING MARKDOWN TABLES for data presentation and comparison. Use tables whenever presenting comparative data, statistics, features, or options. Structure tables with clear headers and aligned columns. Example table format:\n\n| Feature | Description | Pros | Cons |\n|---------|-------------|------|------|\n| Feature 1 | Description 1 | Pros 1 | Cons 1 |\n| Feature 2 | Description 2 | Pros 2 | Cons 2 |",
            name="system",  # 系统消息
        )
    )

    for observation in observations:  # 遍历观察结果
        invoke_messages.append(
            HumanMessage(
                content=f"Below are some observations for the research task:\n\n{observation}",  # 研究任务的观察结果
                name="observation",  # 观察消息
            )
        )
    logger.debug(f"Current invoke messages: {invoke_messages}")  # 记录当前调用消息
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(invoke_messages)  # 调用报告员LLM
    response_content = response.content  # 获取响应内容
    logger.info(f"reporter response: {response_content}")  # 记录报告员响应

    return {"final_report": response_content}  # 返回包含最终报告的字典


def research_team_node(state: State):
    """
    研究团队节点，协作处理任务
    
    参数:
        state: 当前状态
    """
    logger.info("Research team is collaborating on tasks.")  # 研究团队正在协作处理任务
    pass


async def _execute_agent_step(
    state: State, agent, agent_name: str
) -> Command[Literal["research_team"]]:
    """
    执行代理步骤的辅助函数
    
    参数:
        state: 当前状态
        agent: 代理对象
        agent_name: 代理名称
        
    返回:
        命令，指示下一步是研究团队
    """
    current_plan = state.get("current_plan")  # 获取当前计划
    observations = state.get("observations", [])  # 获取观察结果

    # Find the first unexecuted step
    # 查找第一个未执行的步骤
    current_step = None  # 当前步骤
    completed_steps = []  # 已完成的步骤
    for step in current_plan.steps:  # 遍历步骤
        if not step.execution_res:  # 如果步骤没有执行结果
            current_step = step  # 设置当前步骤
            break
        else:
            completed_steps.append(step)  # 添加到已完成的步骤

    if not current_step:  # 如果没有未执行的步骤
        logger.warning("No unexecuted step found")  # 未找到未执行的步骤
        return Command(goto="research_team")  # 返回研究团队命令

    logger.info(f"Executing step: {current_step.title}, agent: {agent_name}")  # 执行步骤

    # Format completed steps information
    # 格式化已完成步骤信息
    completed_steps_info = ""  # 已完成步骤信息
    if completed_steps:  # 如果有已完成的步骤
        completed_steps_info = "# Existing Research Findings\n\n"  # 现有研究发现
        for i, step in enumerate(completed_steps):  # 遍历已完成的步骤
            completed_steps_info += f"## Existing Finding {i + 1}: {step.title}\n\n"  # 现有发现标题
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"  # 现有发现内容

    # Prepare the input for the agent with completed steps info
    # 准备带有已完成步骤信息的代理输入
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{state.get('locale', 'en-US')}"  # 当前任务信息
            )
        ]
    }

    # Add citation reminder for researcher agent
    # 为研究员代理添加引用提醒
    if agent_name == "researcher":  # 如果是研究员代理
        if state.get("resources"):  # 如果有资源
            resources_info = "**The user mentioned the following resource files:**\n\n"  # 用户提到的资源文件
            for resource in state.get("resources"):  # 遍历资源
                resources_info += f"- {resource.title} ({resource.description})\n"  # 资源标题和描述

            agent_input["messages"].append(
                HumanMessage(
                    content=resources_info
                    + "\n\n"
                    + "You MUST use the **local_search_tool** to retrieve the information from the resource files.",  # 必须使用本地搜索工具从资源文件检索信息
                )
            )

        agent_input["messages"].append(
            HumanMessage(
                content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                name="system",
            )
        )

    # Invoke the agent
    default_recursion_limit = 25
    try:
        env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
        parsed_limit = int(env_value_str)

        if parsed_limit > 0:
            recursion_limit = parsed_limit
            logger.info(f"Recursion limit set to: {recursion_limit}")
        else:
            logger.warning(
                f"AGENT_RECURSION_LIMIT value '{env_value_str}' (parsed as {parsed_limit}) is not positive. "
                f"Using default value {default_recursion_limit}."
            )
            recursion_limit = default_recursion_limit
    except ValueError:
        raw_env_value = os.getenv("AGENT_RECURSION_LIMIT")
        logger.warning(
            f"Invalid AGENT_RECURSION_LIMIT value: '{raw_env_value}'. "
            f"Using default value {default_recursion_limit}."
        )
        recursion_limit = default_recursion_limit

    logger.info(f"Agent input: {agent_input}")
    result = await agent.ainvoke(
        input=agent_input, config={"recursion_limit": recursion_limit}
    )

    # Process the result
    response_content = result["messages"][-1].content
    logger.debug(f"{agent_name.capitalize()} full response: {response_content}")

    # Update the step with the execution result
    current_step.execution_res = response_content
    logger.info(f"Step '{current_step.title}' execution completed by {agent_name}")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name=agent_name,
                )
            ],
            "observations": observations + [response_content],
        },
        goto="research_team",
    )


async def _setup_and_execute_agent_step(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type
    2. Creates an agent with the appropriate tools or uses the default agent
    3. Executes the agent on the current step

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    configurable = Configuration.from_runnable_config(config)
    mcp_servers = {}
    enabled_tools = {}

    # Extract MCP server configuration for this agent type
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            if (
                server_config["enabled_tools"]
                and agent_type in server_config["add_to_agents"]
            ):
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name

    # Create and execute agent with MCP tools if available
    if mcp_servers:
        async with MultiServerMCPClient(mcp_servers) as client:
            loaded_tools = default_tools[:]
            for tool in client.get_tools():
                if tool.name in enabled_tools:
                    tool.description = (
                        f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                    )
                    loaded_tools.append(tool)
            agent = create_agent(agent_type, agent_type, loaded_tools, agent_type)
            return await _execute_agent_step(state, agent, agent_type)
    else:
        # Use default tools if no MCP servers are configured
        agent = create_agent(agent_type, agent_type, default_tools, agent_type)
        return await _execute_agent_step(state, agent, agent_type)


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")
    configurable = Configuration.from_runnable_config(config)
    tools = [get_web_search_tool(configurable.max_search_results), crawl_tool]
    retriever_tool = get_retriever_tool(state.get("resources", []))
    if retriever_tool:
        tools.insert(0, retriever_tool)
    logger.info(f"Researcher tools: {tools}")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        tools,
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        [python_repl_tool],
    )
