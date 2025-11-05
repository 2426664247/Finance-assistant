# Financial Agent - 智能金融助手

这是一个基于大型语言模型（LLM）构建的智能金融助手。用户可以通过自然语言与它进行交互，获取金融数据查询、市场分析、知识问答等服务。

## ✨ 功能特性

- **自然语言交互**：像与真人对话一样，提出您的金融问题。
- **实时金融数据**：集成 Tushare 和 yfinance 数据接口，提供股票、指数等实时和历史数据查询。
- **本地知识库**：内置金融知识库，能够解答专业的金融概念和问题。
- **可扩展工具集**：基于 LangChain Agent 架构，可以方便地扩展更多金融工具。
- **Web 界面**：使用 Streamlit 构建，提供友好的用户交互界面。

## 🚀 环境设置与运行

为了保证项目的稳定运行和依赖隔离，强烈建议您使用虚拟环境。

### 1. 克隆项目

```bash
git clone git@github.com:2426664247/Finance-assistant.git
cd Finance-assistant
```

### 2. 创建并激活虚拟环境

本项目推荐使用 Python 3.9 或更高版本。

- **Windows**:
  ```bash
  # 创建虚拟环境
  python -m venv .venv

  # 激活虚拟环境
  .\.venv\Scripts\Activate.ps1
  ```

- **macOS / Linux**:
  ```bash
  # 创建虚拟环境
  python3 -m venv .venv

  # 激活虚拟环境
  source .venv/bin/activate
  ```

激活成功后，您会看到命令行提示符前出现 `(.venv)` 标识。

### 3. 安装项目依赖

所有依赖项都记录在 `financial_agent/requirements.txt` 文件中。

```bash
pip install -r financial_agent/requirements.txt
```

### 4. 配置环境变量

项目需要配置一些 API 密钥才能正常工作。请在项目根目录下创建一个名为 `.env` 的文件，并根据 `financial_agent/.env.example` 的格式填入您的密钥：

```
# .env

# 火山引擎大模型 Access Key
VOLC_ACCESS_KEY="<your-access-key>"
VOLC_SECRET_KEY="<your-secret-key>"

# Tushare 数据接口 Token
TUSHARE_TOKEN="<your-tushare-token>"
```

### 5. 运行应用

一切准备就绪后，在项目根目录下运行以下命令来启动 Streamlit 应用：

```bash
streamlit run app.py
```

应用启动后，您会在终端看到本地访问地址（通常是 `http://localhost:8501`），在浏览器中打开即可开始使用。

## 项目结构

```
.
├── app.py                  # Streamlit 应用主入口
├── financial_agent/        # 金融 Agent 核心逻辑
│   ├── agent.py            # Agent 执行器
│   ├── knowledge_base.csv  # 本地知识库数据
│   ├── knowledge_base_tool.py # 知识库检索引擎
│   ├── requirements.txt    # 项目依赖
│   └── tools/              # Agent 工具集
│       ├── financial_data_tool.py # 金融数据查询工具
│       └── ...
├── .env                    # 环境变量（需自行创建）
├── .gitignore              # Git 忽略文件
└── README.md               # 项目说明文档
```
