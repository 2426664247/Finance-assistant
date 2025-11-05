from langchain.agents.structured_chat.base import create_structured_chat_agent
from langchain.agents.agent import AgentExecutor
from langchain import hub

from ..tools.financial_data_tool import FinancialDataTool
from ..tools.knowledge_base_tool import KnowledgeBaseTool


def create_financial_agent(llm):
    """创建并初始化金融智能体"""

    tools = [FinancialDataTool(), KnowledgeBaseTool(llm=llm)]

    # 使用 LangChain Hub 提示模板（结构化聊天）
    prompt = hub.pull("hwchase17/structured-chat-agent")

    # 创建结构化聊天 Agent
    agent = create_structured_chat_agent(llm, tools, prompt)

    # 包装为 AgentExecutor 执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )

    return agent_executor