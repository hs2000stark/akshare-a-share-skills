"""宏观类数据接口 - 大盘指数"""

import json
import logging
from typing import Any

from . import rate_limiter

logger = logging.getLogger(__name__)


def get_index_daily(symbol: str = "000001", adjust: str = "", use_cache: bool = True) -> dict[str, Any]:
    """获取大盘指数历史K线"""
    if use_cache:
        cache_key = f"index_{symbol}_{adjust}"
        cached = rate_limiter.get_cache().get(cache_key)
        if cached:
            return cached

    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        return _fetch_tx_index(symbol)

    try:
        result = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        raise

    output = {
        "symbol": symbol,
        "source": "tx",
        "data": result,
    }

    if use_cache:
        cache = rate_limiter.get_cache()
        cache.ttl_seconds = 3600
        cache.set(cache_key, output)

    return output


def _fetch_tx_index(symbol: str) -> list:
    """使用腾讯接口获取指数K线"""
    import requests
    
    # 指数代码映射
    if symbol == "000001":
        market = "sh"
    elif symbol == "399001":
        market = "sz"
    else:
        market = "sh"
    
    full_symbol = f"{market}{symbol}"
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={full_symbol},day,,,100,qfqa"
    
    resp = requests.get(url, timeout=15)
    data = resp.json()
    
    day_data = data['data'][full_symbol]['day']
    
    result = []
    for item in day_data:
        if isinstance(item, list):
            result.append({
                '日期': item[0],
                '开盘': item[1],
                '收盘': item[2],
                '最高': item[3],
                '最低': item[4],
                '成交量': item[5],
            })
    
    return result


def get_index_spot(symbols=None) -> dict[str, Any]:
    """获取指数实时行情"""
    if not symbols:
        symbols = ["000001", "399001"]
    
    rate_limiter.get_rate_limiter().wait()
    
    result = []
    for symbol in symbols:
        try:
            data = _fetch_tx_index(symbol)
            if data:
                result.append({
                    "symbol": symbol,
                    "latest": data[-1] if data else None
                })
        except:
            pass
    
    return {"data": result}


def get_market_summary(market: str = "sse") -> dict[str, Any]:
    """市场总貌 - 暂不可用"""
    return {"error": "市场总貌接口暂不可用（push2.eastmoney.com 被限制）"}


def get_market_fund_flow() -> dict[str, Any]:
    """市场资金流向 - 暂不可用"""
    return {"error": "资金流向接口暂不可用（push2.eastmoney.com 被限制）"}


def get_hsgt_hist(start: str = None, end: str = None) -> dict[str, Any]:
    """沪深港通 - 暂不可用"""
    return {"error": "沪深港通接口暂不可用（push2.eastmoney.com 被限制）"}


def get_sector_fund_flow(flow_type: str = "industry") -> dict[str, Any]:
    """板块资金流向 - 暂不可用"""
    return {"error": "板块资金流向接口暂不可用"}


def get_board_spot(board_type: str = "industry") -> dict[str, Any]:
    """板块行情 - 暂不可用"""
    return {"error": "板块行情接口暂不可用"}
