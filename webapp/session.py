import streamlit as st
import os
import json
import uuid
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
    """加载指定的聊天历史记录到当前会话"""
    # 在加载前，先保存当前可能正在进行的对话
    save_chat_history(st.session_state.current_session_id, get_current_messages())

    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            chat_history = json.load(f)
            # 修复：将加载的列表作为值存入字典，而不是覆盖整个字典
            st.session_state.messages[session_id] = chat_history
            # 修复：更新 current_session_id 以切换到加载的会话
            st.session_state.current_session_id = session_id
            st.rerun()

def delete_chat_history(session_id):
    """删除指定的聊天历史记录文件"""
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        # st.rerun() # The rerun is already in ui.py