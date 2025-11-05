import streamlit as st
from financial_agent.core.agent import create_financial_agent
from financial_agent.core.llm_adapter import VolcanoLLM
from webapp.session import (
    initialize_session_state,
    get_current_messages,
    add_message_to_current_session
)
from webapp.ui import (
    render_page_config,
    render_sidebar,
    render_chat_messages,
    render_agent_response
)

# --- 1. 页面与会话初始化 ---
render_page_config()
initialize_session_state()

# --- 2. 智能体初始化 ---
@st.cache_resource
def get_agent():
    """缓存并返回金融智能体实例"""
    llm = VolcanoLLM(streaming=True)
    return create_financial_agent(llm)
agent = get_agent()

# --- 3. 渲染侧边栏 ---
render_sidebar()

# --- 4. 渲染主聊天界面 ---

# 获取当前对话的聊天记录
current_messages = get_current_messages()

# 显示历史消息
render_chat_messages(current_messages)

# 响应用户的新输入
if prompt := st.chat_input("请输入您的问题..."):
    # a. 将用户消息添加到会话状态并显示
    add_message_to_current_session("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # b. 获取并流式显示智能体的回复
    # 注意：此时 current_messages 已经包含了最新的用户消息
    full_response = render_agent_response(agent, prompt, current_messages)
    
    # c. 将完整的智能体回复添加到会话状态
    add_message_to_current_session("assistant", full_response)