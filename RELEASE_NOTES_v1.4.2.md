# 发布说明：v1.4.2

发布日期：2025-11-10
标签：`v1.4.2`
提交范围：合并至 `master`（79edf58 → 6a084dc）

## 主要更新
- 增强美股数据抓取逻辑：
  - 先使用 `yfinance.download` 获取日线数据；
  - 若为空，二次尝试 `yf.Ticker(symbol).history`；
  - 显著提升 AAPL、MSFT 等美股标的在限流和网络波动下的成功率。
- 新增备用回退数据源：
  - 增加 `pandas-datareader==0.10.0`，当 yfinance 失败时回退至 `Stooq` 数据源；
  - 覆盖 yfinance 返回空或异常的边界情况。
- 修复工具返回值类型：
  - `KnowledgeBaseTool._run` 统一返回 `str`，避免 `HumanMessage` 的 Pydantic 验证错误。
- 文档与依赖：
  - 新增 `CHANGELOG.md` 并在 `README.md` 标注当前版本为 `v1.4.2`；
  - `financial_agent/requirements.txt` 追加 `pandas-datareader==0.10.0`。

## 迁移注意
- LangChain 的部分导入路径在未来版本将弃用：
  - `vectorstores` 与 `document_loaders` 请迁移至 `langchain_community.*`；
  - 已对齐当前版本，保留兼容性。
- Windows 环境建议将 `requirements.txt` 与 `.env` 保存为 UTF-8 避免编码问题。

## 安装与运行（摘要）
1. 激活虚拟环境（Python 3.10）：
   - Windows：`python -m venv .venv` → `\.venv\Scripts\Activate.ps1`
2. 安装依赖：
   - `pip install -r financial_agent/requirements.txt`
3. 环境变量（`financial_agent/configs/.env`）：
   - `ARK_API_KEY`、`ARK_MODEL_ID`、`ARK_EMBEDDING_MODEL_ID`、`ARK_TITLE_MODEL_ID`
   - `TUSHARE_TOKEN`（A 股推荐）
4. 启动：
   - `python -m streamlit run app.py`（默认端口 localhost:8501/8503）

## 发行包
- `Finance-assistant-v1.4.2.zip`（基于标签 `v1.4.2` 的干净归档，不含 Git 历史）

---
如需进一步将 Release 自动化（CI 推送 tag 自动创建 GitHub Release 并上传 zip），建议后续加入 GitHub Actions 工作流。