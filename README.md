# Financial-Assistant: 您的个人智能金融助手

Financial-Assistant 是一个基于大型语言模型（LLM）构建的智能金融对话助手。它结合了先进的自然语言处理能力和实时的金融数据分析工具，旨在为用户提供专业、便捷的金融信息查询和分析服务。

## 核心功能

- **多轮对话**：支持流畅、有上下文记忆的多轮对话，能够深入理解用户意图。
- **金融数据分析**：集成 Tushare 和 yfinance 数据接口，可实时查询和分析股票行情、财务数据等。
- **知识库问答**：内置金融知识库，能够解答专业的金融概念和市场问题。
- **智能历史记录**：
    - **动态命名**：对话结束后，后台自动调用轻量 LLM 为对话生成精准标题，优化查阅体验。
    - **便捷管理**：支持在界面上直接删除历史对话记录。
- **时间感知**：智能体能够获取并理解当前时间，为提供时效性信息提供支持。
- **模型调用监控**：所有对大模型的调用（主模型、标题生成模型）都会在终端打印详细日志，便于调试和监控。

## 技术架构

本项目采用分层架构，将前端展示、后端逻辑和核心智能完全解耦，保证了代码的清晰度和可维护性。

```
/
├── app.py                  # Streamlit 应用主入口
├── chat_history/           # 存放聊天记录的目录
├── financial_agent/        # 智能体核心逻辑
│   ├── configs/
│   │   └── .env.example    # 环境变量示例文件
│   ├── core/
│   │   ├── agent.py        # LangChain Agent 的封装和实现
│   │   └── llm_adapter.py  # 火山方舟 LLM 和 Embedding 模型适配器
│   ├── tools/              # Agent 可使用的工具
│   │   ├── financial_data_tool.py # 金融数据查询工具
│   │   └── knowledge_base_tool.py # 知识库检索工具
│   └── requirements.txt    # Python 依赖项
└── webapp/                 # Streamlit 前端应用
    ├── session.py          # 会话状态管理（包括智能命名逻辑）
    └── ui.py               # UI 组件和布局
```

### 关键组件详解

1.  **`llm_adapter.py`**:
    *   **`VolcanoLLM`**: 继承自 LangChain 的 `LLM` 基类，适配火山引擎方舟（VolcEngine ARK）服务。它支持在初始化时动态传入 `model_id`，从而允许在不同场景（如主对话、标题生成）使用不同的模型。
    *   **`VolcanoEmbeddings`**: 适配火山方舟的 Embedding 模型，用于知识库的文本向量化。
    *   **日志系统**: 在 `_call` (同步) 和 `_stream` (流式) 方法中集成了详细的日志输出，将模型 ID 和返回内容打印到终端，实现了完全的调用透明化。

2.  **`agent.py`**:
    *   基于 LangChain 的 `ConversationalChatAgent` 构建，实现了具备对话记忆的 ReAct (Reasoning and Acting) 风格智能体。
    *   它能够根据用户问题，自主决策并调用 `financial_data_tool` 或 `knowledge_base_tool` 来完成任务。

3.  **`session.py`**:
    *   **`generate_chat_title`**: 对话进行到第二轮时，在后台线程中被调用。它会请求一个独立的、轻量的 LLM（由 `ARK_TITLE_MODEL_ID` 指定）为当前对话生成一个简洁的标题，并缓存结果。
    *   **`save_chat_history`**: 当用户点击“新对话”时触发。它会优先使用缓存中的标题来保存聊天记录，实现了“零等待”的智能命名体验。如果缓存不存在，则会同步调用模型生成标题。

## 本地部署指南

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/Financial-Assistant.git
cd Financial-Assistant
```

### 2. 配置环境变量

在 `financial_agent/configs/` 目录下，复制 `.env.example` 文件并重命名为 `.env`。

```bash
cp financial_agent/configs/.env.example financial_agent/configs/.env
```

然后，编辑 `.env` 文件，填入您的个人密钥和模型信息。

```ini
# 火山方舟 API Key (从火山引擎控制台获取)
ARK_API_KEY="YOUR_ARK_API_KEY"

# Tushare Token (从 Tushare 官网个人主页获取)
TUSHARE_TOKEN="YOUR_TUSHARE_TOKEN"

# --- 模型 ID 配置 ---
# 主对话模型 (推荐使用性能强劲的模型)
ARK_MODEL_ID="ep-20240701185338-5q5f7"

# 历史记录标题生成模型 (推荐使用响应速度快的轻量模型)
ARK_TITLE_MODEL_ID="ep-20251105151025-g4n4m"

# Embedding 模型 (用于知识库向量化)
ARK_EMBEDDING_MODEL_ID="embedding-model-id"
```

### 3. 安装依赖

建议在虚拟环境中安装，以避免包版本冲突。

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

pip install -r financial_agent/requirements.txt
```

### 4. 运行应用

```bash
streamlit run app.py
```

应用启动后，浏览器将自动打开 `http://localhost:8501`，您即可开始使用。