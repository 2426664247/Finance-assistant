from langchain.tools import BaseTool
import yfinance as yf
import pandas as pd
from pydantic import BaseModel, Field
from typing import Type
import os
from pathlib import Path
from datetime import datetime
import tushare as ts
try:
    # 作为备用数据源（避免 yfinance 限流）
    from pandas_datareader import data as pdr
    HAS_PDR = True
except Exception:
    HAS_PDR = False
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except Exception:
    HAS_DOTENV = False
from datetime import datetime
try:
    # 作为备用数据源（避免 yfinance 限流）
    from pandas_datareader import data as pdr
    HAS_PDR = True
except Exception:
    HAS_PDR = False

class StockQueryInput(BaseModel):
    """获取股票日K线数据的输入模型"""
    symbol: str = Field(description="股票代码，例如 '600519.SS' 表示贵州茅台")
    start_date: str = Field(description="开始日期，格式为 'YYYY-MM-DD'")
    end_date: str = Field(description="结束日期，格式为 'YYYY-MM-DD'")

class FinancialDataTool(BaseTool):
    name: str = "Financial Data Retrieval"
    description: str = "用于获取股票的日K线数据。输入应为一个包含'symbol', 'start_date', 'end_date'的字典。"
    args_schema: Type[BaseModel] = StockQueryInput

    def _run(self, symbol: str, start_date: str, end_date: str) -> str:
        """执行获取日K线数据的核心逻辑。返回纯文本字符串以兼容 LangChain Agent。"""
        # 若为 A 股代码，优先使用 Tushare（更稳定）
        if self._is_china_equity(symbol):
            ts_init_ok = self._init_tushare()
            ts_code = self._to_ts_code(symbol)
            if ts_init_ok and ts_code:
                ts_result = self._fetch_with_tushare(ts_code, start_date, end_date)
                if ts_result:
                    return ts_result
                # 若 Tushare 返回空或失败，继续尝试国际源
        # 国际源（yfinance），失败则回退到 Stooq
        try:
            data = yf.download(symbol, start=start_date, end=end_date)
            if data is not None and not data.empty:
                return f"成功获取 {symbol} 从 {start_date} 到 {end_date} 的日K线数据：\n{data.to_string()}"
            result = self._fallback_fetch(symbol, start_date, end_date)
            return result
        except Exception as e:
            result = self._fallback_fetch(symbol, start_date, end_date, err=e)
            return result

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")

    def _init_tushare(self) -> bool:
        """初始化 Tushare TOKEN。
        直接从环境变量读取 TUSHARE_TOKEN。
        """
        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            # 如果环境变量中没有找到 TUSHARE_TOKEN，则尝试从 .env 文件加载
            try:
                if HAS_DOTENV:
                    # .env 文件应该在项目根目录的 configs 文件夹下
                    dotenv_path = Path(__file__).resolve().parents[2] / "configs" / ".env"
                    if dotenv_path.exists():
                        load_dotenv(dotenv_path=dotenv_path)
                        token = os.getenv("TUSHARE_TOKEN")
            except Exception:
                pass  # 静默失败

        if not token:
            # 最终还是没有 TOKEN，则初始化失败
            return False
        
        try:
            ts.set_token(token)
            return True
        except Exception:
            return False

    def _is_china_equity(self, symbol: str) -> bool:
        """判断是否为中国 A 股或北交所代码。支持 '600519', '600519.SH', '600519.SS' 等格式。"""
        s = symbol.upper().strip()
        # 数字 6 位直接认定为 A 股
        if s.isdigit() and len(s) == 6:
            return True
        # 含交易所后缀
        if ".SH" in s or ".SZ" in s or ".BJ" in s or ".SS" in s:
            return True
        return False

    def _to_ts_code(self, symbol: str) -> str | None:
        """将输入代码转换为 Tushare ts_code 格式，例如 '600519.SH'。
        规则：
        - 以 '6' 开头 -> 上交所 'SH'
        - 以 '0' 或 '3' 开头 -> 深交所 'SZ'
        - 以 '8' 或 '4' 开头 -> 北交所 'BJ'
        - 带 '.SS' 的 -> 上交所 'SH'
        - 已带 '.SH/.SZ/.BJ' 保持不变
        """
        s = symbol.upper().strip()
        if ".SS" in s:
            base = s.replace(".SS", "")
            if base.isdigit():
                return f"{base}.SH"
            return None
        if any(s.endswith(suf) for suf in [".SH", ".SZ", ".BJ"]):
            return s
        # 纯数字处理
        if s.isdigit() and len(s) == 6:
            if s[0] == "6":
                return f"{s}.SH"
            if s[0] in ("0", "3"):
                return f"{s}.SZ"
            if s[0] in ("8", "4"):
                return f"{s}.BJ"
        return None

    def _fetch_with_tushare(self, ts_code: str, start_date: str, end_date: str) -> str | None:
        """使用 Tushare 获取 A 股日线数据。返回格式化字符串，失败返回 None。"""
        try:
            # 直接从环境读取 TOKEN，避免 set_token 未生效问题
            token = os.getenv("TUSHARE_TOKEN")
            pro = ts.pro_api(token) if token else ts.pro_api()
            sd = start_date.replace("-", "")
            ed = end_date.replace("-", "")
            df = pro.daily(ts_code=ts_code, start_date=sd, end_date=ed)
            if df is None or df.empty:
                return None
            # Tushare 返回按 trade_date 倒序，一般需要按日期升序展示
            df = df.sort_values(by="trade_date").rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "vol": "Volume",
            })
            # 将 trade_date 转换为 DatetimeIndex 并格式化
            df["trade_date"] = pd.to_datetime(df["trade_date"])
            df = df.set_index("trade_date")
            return f"(Tushare)成功获取 {ts_code} 从 {start_date} 到 {end_date} 的日K线数据：\n{df[['Open','High','Low','Close','Volume']].to_string()}"
        except Exception:
            return None

    def _fallback_fetch(self, symbol: str, start_date: str, end_date: str, err: Exception | None = None) -> str:
        """当 yfinance 限流或返回空数据时，尝试使用 Stooq 数据源回退"""
        if not HAS_PDR:
            return (
                f"获取数据失败，且备用数据源不可用。错误: {err}. "
                f"如需更稳定的 A 股数据，请在 configs/.env 配置 TUSHARE_TOKEN 并使用 Tushare。"
            )

        try:
            # Stooq 使用 'YYYY-MM-DD' 日期格式，符号如 'AAPL'、'MSFT'；不支持 A 股代码
            # 转换日期，确保格式正确
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            df = pdr.DataReader(symbol, "stooq", start=start_dt, end=end_dt)
            if df is None or df.empty:
                return (
                    f"yfinance 获取失败且 Stooq 数据为空。"
                    f"请尝试缩短日期范围或更换标的（如 AAPL、MSFT），"
                    f"或改用 Tushare 获取 A 股数据（需配置 TUSHARE_TOKEN）。原始错误: {err}"
                )
            # 与 yfinance 字段对齐展示
            df = df.sort_index()
            return f"(回退)成功获取 {symbol} 从 {start_date} 到 {end_date} 的日K线数据：\n{df.to_string()}"
        except Exception as e2:
            return (
                f"yfinance 获取失败且 Stooq 回退失败。请稍后重试或更换数据源。"
                f"yfinance错误: {err}; Stooq错误: {e2}"
            )