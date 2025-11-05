import streamlit as st
import os
import json
from datetime import datetime

# --- 文件夹设置 ---
HISTORY_DIR = "chat_history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# --- 会话状态管理 ---

def get_new_session_id():
    """生成一个新的、基于时间的会话ID"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save_chat_history(session_id, messages):
    """将聊天记录保存到JSON文件"""
    if not messages:
        return
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def initialize_session_state():
    """初始化 Streamlit 的 session_state"""
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = get_new_session_id()
        st.session_state.messages[st.session_state.current_session_id] = []

def get_current_messages():
    """获取当前会话的聊天记录"""
    return st.session_state.messages.get(st.session_state.current_session_id, [])

def add_message_to_current_session(role, content):
    """向当前会话添加一条消息"""
    current_messages = get_current_messages()
    current_messages.append({"role": role, "content": content})
    st.session_state.messages[st.session_state.current_session_id] = current_messages

def handle_new_chat():
    """处理“新对话”按钮的点击事件"""
    save_chat_history(st.session_state.current_session_id, get_current_messages())
    st.session_state.current_session_id = get_new_session_id()
    st.session_state.messages[st.session_state.current_session_id] = []
    st.rerun()

def load_chat_history(session_id):
    """加载指定的历史聊天记录"""
    save_chat_history(st.session_state.current_session_id, get_current_messages())
    
    st.session_state.current_session_id = session_id
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        st.session_state.messages[session_id] = json.load(f)
    st.rerun()