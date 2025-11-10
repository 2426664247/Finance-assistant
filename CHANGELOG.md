# Changelog

All notable changes to this project will be documented in this file.

## v1.4.2 — 2025-11-10

- 增强美股数据抓取逻辑：优先使用 `yfinance.download`，失败时二次尝试 `Ticker.history`。
- 新增备用数据源：添加 `pandas-datareader`，当 yfinance 失败时回退到 `Stooq` 数据源。
- 修复工具返回值类型：`KnowledgeBaseTool._run` 改为返回纯字符串，避免 `HumanMessage` 的 Pydantic 验证错误。
- 依赖更新：`requirements.txt` 增加 `pandas-datareader==0.10.0`。
- 文档：说明版本信息，并在 README 中链接到此变更日志。