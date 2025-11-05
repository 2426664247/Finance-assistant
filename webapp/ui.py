import streamlit as st
import os
from langchain.schema import HumanMessage, AIMessage
from .session import handle_new_chat, load_chat_history, HISTORY_DIR

def render_page_config():
    """设置页面配置和标题"""
    st.set_page_config(page_title="金融咨询智能体", page_icon="💰", layout="wide")
    st.title("💰 金融咨询智能体")
    st.caption("由 LangChain 和火山方舟模型驱动")

def render_sidebar():
    """渲染侧边栏，包括新对话按钮和历史记录"""
    with st.sidebar:
        st.header("对话管理")
        if st.button("➕ 新对话"):
            handle_new_chat()

        st.header("历史记录")
        history_files = sorted(os.listdir(HISTORY_DIR), reverse=True)
        for filename in history_files:
            session_id = filename.split('.')[0]
            if st.button(session_id, key=f"history_{filename}"):
                load_chat_history(session_id)

def render_chat_messages(messages):
    """从历史记录中显示聊天消息"""
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def render_agent_response(agent, prompt, current_messages):
    """处理用户输入，获取并流式显示智能体的回复"""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        full_response = ""
        output_started = False
        
        # 为智能体准备对话历史
        chat_history = []
        for msg in current_messages[:-1]: # 排除刚刚添加的用户最新消息
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))
        
        try:
            status_placeholder.text("思考中...")
            for chunk in agent.stream({"input": prompt, "chat_history": chat_history}):
                if "actions" in chunk and not output_started:
                    for action in chunk["actions"]:
                        status_placeholder.text(f"查询工具: {action.tool}...")
                elif "steps" in chunk and not output_started:
                    status_placeholder.text("分析中...")
                elif "output" in chunk and chunk["output"]:
                    if not output_started:
                        status_placeholder.empty()
                        output_started = True
                    
                    full_response += chunk["output"]
                    message_placeholder.markdown(full_response + "▌")
        finally:
            status_placeholder.empty()
            message_placeholder.markdown(full_response)
            
    return full_response