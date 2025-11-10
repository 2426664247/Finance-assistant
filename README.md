# 金融咨询智能体（Financial Agent）
版本：v1.4.2

一个基于 Streamlit 与 LangChain 的金融咨询智能体，支持基础金融问答、知识库检索以及股票日K数据查询。文档面向外部读者，提供通用的安装、配置与运行说明。

## ✨ 功能特性

- **自然语言交互**：像与真人对话一样，提出您的金融问题。
- **实时金融数据**：集成 Tushare 和 yfinance 数据接口，提供股票、指数等实时和历史数据查询。
- **本地知识库**：内置金融知识库，能够解答专业的金融概念和问题。
- **可扩展工具集**：基于 LangChain Agent 架构，可以方便地扩展更多金融工具。
- **Web 界面**：使用 Streamlit 构建，提供友好的用户交互界面。

## 🚀 环境设置与运行（当前版本：v1.4.2）

更多版本改动请参见 [`CHANGELOG.md`](./CHANGELOG.md)。

为了保证项目的稳定运行和依赖隔离，强烈建议您使用虚拟环境。本项目的开发和测试环境基于以下精确版本，为确保最佳兼容性，请遵循此配置。

### 1. 基础环境

- **Python 版本**: `3.10.19`

请确保您的系统中已安装 Python 3.10.19。您可以从 [Python 官网](https://www.python.org/downloads/release/python-31019/) 下载对应的安装包。

### 2. 克隆项目

```bash
git clone git@github.com:2426664247/Finance-assistant.git
cd Finance-assistant
```

### 3. 创建并激活虚拟环境

- **Windows**:
  ```bash
  # 使用指定的 Python 版本创建虚拟环境
  python -m venv .venv

  # 激活虚拟环境
  .\.venv\Scripts\Activate.ps1
  ```

- **macOS / Linux**:
  ```bash
  # 使用指定的 Python 版本创建虚拟环境
  python3 -m venv .venv

  # 激活虚拟环境
  source .venv/bin/activate
  ```

激活成功后，您会看到命令行提示符前出现 `(.venv)` 标识。

### 4. 安装项目依赖

所有依赖项及其精确版本都记录在 `financial_agent/requirements.txt` 文件中。该文件通过 `pip freeze` 生成，锁定了所有直接及间接依赖，以确保在任何环境下都能创建 100% 一致的运行环境。

```bash
pip install -r financial_agent/requirements.txt
```

这将安装项目所需的所有软件包，保证了版本的精确匹配和项目的稳定性。

### 5. 配置环境变量

项目需要配置一些 API 密钥才能正常工作。请在项目根目录下创建一个名为 `.env` 的文件，并根据 `financial_agent/.env.example` 的格式填入您的密钥：

```
# .env

# 火山引擎大模型 Access Key
VOLC_ACCESS_KEY="<your-access-key>"
VOLC_SECRET_KEY="<your-secret-key>"

# Tushare 数据接口 Token
TUSHARE_TOKEN="<your-tushare-token>"
```

### 6. 运行应用

一切准备就绪后，在项目根目录下运行以下命令来启动 Streamlit 应用：

```bash
streamlit run app.py
```

应用启动后，您会在终端看到本地访问地址（通常是 `http://localhost:8501`），在浏览器中打开即可开始使用。

## 项目结构

## 目录结构（简要）
```
.
├── app.py                     # Streamlit 入口
├── financial_agent/
│   ├── core/
│   │   ├── agent.py           # 智能体构建（规则路由版）
│   │   └── llm_adapter.py     # 模型与向量适配
│   ├── tools/
│   │   ├── financial_data_tool.py    # 股票日K数据工具
│   │   └── knowledge_base_tool.py    # 知识库检索工具
│   ├── financial_knowledge_base.csv  # 知识库数据
│   └── configs/.env           # 环境变量配置
└── webapp/
    ├── ui.py                  # 页面与交互（流式显示）
    └── session.py             # 会话管理与历史记录
```

## 安装与配置
推荐在独立的虚拟环境中安装运行（Conda 或 venv 均可）。依赖已在 `financial_agent/requirements.txt` 中精确锁定，便于复现。

1) 创建并激活环境（示例为 Conda）：
```
conda create -n financial_agent python=3.10
conda activate financial_agent
```

2) 安装依赖：
```
pip install -r financial_agent/requirements.txt
```
（requirements 已精确锁定到当前运行的版本，包括 `langchain==0.2.17`、`langchain-community==0.2.19`、`langchain-core==0.2.43`、`langchain-text-splitters==0.2.4`、`streamlit==1.51.0`、`faiss-cpu==1.7.4`、`yfinance==0.2.66`、`pandas==2.1.4`、`numpy==1.26.2`、`pandas-datareader==0.10.0`、`tushare==1.4.24`、`python-dotenv==1.0.0`、`volcengine-python-sdk[ark]==4.0.31`。）

3) 配置环境变量（`financial_agent/configs/.env`）：
```
ARK_API_KEY=your_api_key
ARK_MODEL_ID=your_chat_model_id
ARK_EMBEDDING_MODEL_ID=your_embedding_model_id
ARK_TITLE_MODEL_ID=your_title_model_id
TUSHARE_TOKEN=your_tushare_token
```

## 启动
环境激活后，在项目根目录运行（如需在服务器后台运行，请参考 Streamlit 文档）：
```
streamlit run app.py
```
启动成功后，浏览器访问：
```
http://localhost:8501
```

## 使用示例
- 金融数据查询（A 股或国际标的）：
  - 600519 从 2024-01-01 到 2024-03-31 的日K线
  - AAPL 从 2023-11-01 到 2023-12-01 的日K线
- 知识库问答：
  - ETF是什么？有哪些风险？
- 通用问答：
  - 例如“介绍一下量化交易的基本流程”，系统会注入当前日期上下文后回答。

## 实现说明
- 智能体采用“规则路由版”：
  - 优先识别“股票代码+日期范围”→ 调用金融数据工具
  - 否则尝试知识库检索 → 用 LLM 生成回答
  - 最后回退为通用 LLM 回复
- 工具返回统一为纯字符串，避免消息校验错误；UI 保持 `.stream(...)` 流式渲染。
- 依赖导入已对齐到新版结构：
  - `FAISS` 使用 `langchain_community.vectorstores`
  - `CSVLoader` 使用 `langchain_community.document_loaders`
  - 文本切分器使用 `langchain_text_splitters`
  - 消息类型使用 `langchain_core.messages`

## 常见问题（FAQ）
- A 股数据为空或报错：
  - 优先在 `.env` 配置 `TUSHARE_TOKEN`；否则将回退到 yfinance 或 Stooq。
- yfinance 限流：
  - 缩短日期范围、稍后重试，或依赖 Tushare 获取 A 股数据。
- CSV 路径与编码：
  - 使用相对路径与 UTF-8 编码加载 `financial_knowledge_base.csv`；确认文件存在且编码正确。
- LangSmith 提示：
  - 若日志提示缺少 LangSmith API Key，可忽略，不影响本地功能。
- Windows 编码：
  - 请确保 `.env` 与 `requirements.txt` 使用 UTF-8 编码保存，避免 GBK 读取问题。
- 消息校验错误：
  - 工具返回已统一为 `str`；若仍有问题，清理缓存并重启应用。

## 可选演进
- 迁移到“新式 Agent（自动工具绑定）”：
  - 新增聊天模型适配，支持原生 `.bind_tools`/函数调用
  - 使用 `create_agent` 或 LangGraph 的代理图，实现自动工具选择与结构化输出
  - 保持现有 UI 的事件流与 `.stream(...)` 行为

## 复现步骤（一步到位）
- 创建虚拟环境并激活（示例：Conda + Python 3.10）：
  - `conda create -n financial_agent python=3.10`
  - `conda activate financial_agent`
- 安装依赖（已精确版本锁定）：
  - `pip install -r financial_agent/requirements.txt`
- 配置环境变量（`financial_agent/configs/.env`）：
  - `ARK_API_KEY`、`ARK_MODEL_ID`、`ARK_EMBEDDING_MODEL_ID`、`ARK_TITLE_MODEL_ID`
  - 可选 `TUSHARE_TOKEN`
- 运行应用：
  - `streamlit run app.py`
- 验证：
  - 侧边栏“历史记录”只在创建新对话后显示上一会话标题（使用轻量模型生成）；
  - 金融数据查询示例（A 股/国际）：`600519 从 2024-01-01 到 2024-03-31 的日K线`、`AAPL 从 2023-11-01 到 2023-12-01 的日K线`；
  - 知识库问答示例：`ETF是什么？有哪些风险？`。
