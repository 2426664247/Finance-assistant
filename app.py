import streamlit as st
from financial_agent.core.agent import create_financial_agent
from financial_agent.core.llm_adapter import VolcanoLLM
from langchain.schema import HumanMessage, AIMessage

# --- 页面配置与标题 ---
st.set_page_config(page_title="金融咨询智能体", page_icon="💰", layout="wide")
st.title("💰 金融咨询智能体")
st.caption("由 LangChain 和火山方舟模型驱动")

# --- 智能体初始化 ---
@st.cache_resource
def get_agent():
    llm = VolcanoLLM(streaming=True)
    return create_financial_agent(llm)
agent = get_agent()

# --- 会话状态初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 1. 从历史记录中显示聊天消息 (标准模式)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. 响应用户的新输入 (标准模式)
if prompt := st.chat_input("请输入您的问题..."):
    # a. 在聊天容器中显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    # b. 将用户消息添加到聊天记录
    st.session_state.messages.append({"role": "user", "content": prompt})

    # c. 在聊天容器中显示智能体回复
    with st.chat_message("assistant"):
        # 创建用于流式显示内容的占位符
        message_placeholder = st.empty()
        # 创建用于显示 "思考中..." 等状态的占位符
        status_placeholder = st.empty()
        
        full_response = ""
        output_started = False
        
        # 为智能体准备对话历史 (不包含当前的用户输入)
        chat_history = []
        for msg in st.session_state.messages[:-1]:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))
        
        try:
            status_placeholder.text("思考中...")
            # 传入 input 和 chat_history
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
                    message_placeholder.markdown(full_response + "▌") # 打字光标效果
        finally:
            status_placeholder.empty()
            message_placeholder.markdown(full_response) # 显示最终结果

    # d. 将完整的智能体回复添加到聊天记录
    st.session_state.messages.append({"role": "assistant", "content": full_response})