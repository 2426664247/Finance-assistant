import streamlit as st
import os
import json
import uuid
from datetime import datetime
from typing import List

from financial_agent.core.llm_adapter import VolcanoLLM

# --- 文件夹设置 ---
HISTORY_DIR = "chat_history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# --- 会话状态管理 ---

def get_new_session_id():
    """生成一个新的、基于时间的会话ID"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save_chat_history(session_id, messages, finalize: bool = False):
    """将聊天记录保存到JSON文件。
    - 仅在 finalize=True 时写入文件并生成标题（用户点击“新对话”时）。
    - finalize=False 时不写入文件（避免当前会话出现在历史列表）。
    """
    if messages is None:
        return
    if not finalize:
        # 不持久化当前会话，直到创建新对话时再写入
        return
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    title = _generate_title_safe(messages)
    payload = {"title": title, "messages": messages}
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)

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
    # 仅保存消息，保持现有标题不变（不动态更新）
    save_chat_history(st.session_state.current_session_id, current_messages, finalize=False)

def handle_new_chat():
    """处理“新对话”按钮的点击事件"""
    # 在创建新会话前，最终生成并写入当前会话标题
    save_chat_history(st.session_state.current_session_id, get_current_messages(), finalize=True)
    st.session_state.current_session_id = get_new_session_id()
    st.session_state.messages[st.session_state.current_session_id] = []
    st.rerun()

def load_chat_history(session_id):
    """加载指定的聊天历史记录到当前会话"""
    # 在加载前，先保存当前可能正在进行的对话
    # 仅保存消息，不更新标题
    save_chat_history(st.session_state.current_session_id, get_current_messages(), finalize=False)

    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            chat_history = json.load(f)
            # 兼容两种格式：列表 或 {title, messages}
            if isinstance(chat_history, list):
                messages = chat_history
            elif isinstance(chat_history, dict):
                messages = chat_history.get("messages", [])
            else:
                messages = []
            st.session_state.messages[session_id] = messages
            # 修复：更新 current_session_id 以切换到加载的会话
            st.session_state.current_session_id = session_id
            st.rerun()

def delete_chat_history(session_id):
    """删除指定的聊天历史记录文件"""
    file_path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        # st.rerun() # The rerun is already in ui.py


def _generate_title_safe(messages: List[dict]) -> str:
    """动态生成会话标题：使用轻量模型 ARK_TITLE_MODEL_ID；若不可用则回退。"""
    try:
        # 环境变量读取（若不存在则回退）
        title_model_id = os.getenv("ARK_TITLE_MODEL_ID")
        api_key = os.getenv("ARK_API_KEY")
        if not title_model_id or not api_key:
            # 简单回退：取最近一条用户消息或默认标题
            for m in reversed(messages):
                if m.get("role") == "user" and m.get("content"):
                    return _truncate_title(m["content"]) or "新的对话"
            return "新的对话"

        # 构造标题提示：仅取最近若干条消息，避免长文本
        recent = messages[-6:] if messages else []
        convo = "\n".join([f"{m.get('role','')}: {str(m.get('content',''))}" for m in recent])
        prompt = (
            "请基于以下对话内容，生成一个简洁的中文对话标题（不超过12个字，避免标点与引号，突出主题要点）：\n"
            f"{convo}\n"
            "只输出标题本身。"
        )
        llm = VolcanoLLM(streaming=False, model_id=title_model_id)
        title = llm.invoke(prompt)
        return _truncate_title(title) or "新的对话"
    except Exception:
        # 任意异常回退
        for m in reversed(messages):
            if m.get("role") == "user" and m.get("content"):
                return _truncate_title(m["content"]) or "新的对话"
        return "新的对话"


def _truncate_title(text: str) -> str:
    """裁剪标题到约12字，去除多余空白与换行。"""
    if not isinstance(text, str):
        return ""
    t = text.strip().replace("\n", " ")
    return t[:12]