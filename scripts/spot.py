"""实时行情查询模块 - 腾讯接口"""

import json
import logging
from typing import Any

from . import rate_limiter

logger = logging.getLogger(__name__)


def get_spot(symbol: str, source: str = "tx", use_cache: bool = True) -> dict[str, Any]:
    """获取指定股票的实时报价"""
    if use_cache:
        cache_key = f"spot_{symbol}_{source}"
        cached = rate_limiter.get_cache().get(cache_key)
        if cached:
            return cached

    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        return _fetch_tx(symbol)

    try:
        result = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        raise

    output = {
        "symbol": symbol,
        "source": "tx",
        "quote": result,
    }

    if use_cache:
        cache = rate_limiter.get_cache()
        cache.ttl_seconds = 30
        cache.set(cache_key, output)

    return output


def _fetch_tx(symbol: str) -> dict[str, Any]:
    """使用腾讯接口获取实时行情"""
    import requests
    
    if symbol.startswith('6'):
        market = 'sh'
    elif symbol.startswith('0') or symbol.startswith('3'):
        market = 'sz'
    else:
        market = 'sh'
    
    full_symbol = f"{market}{symbol}"
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={full_symbol},day,,,1,qfqa"
    
    resp = requests.get(url, timeout=10)
    data = resp.json()
    
    qt = data['data'][full_symbol]['qt'].get(full_symbol, [])
    if not qt:
        raise ValueError(f"无法获取 {symbol} 的行情数据")
    
    result = {
        '股票代码': qt[2],
        '股票名称': qt[1],
        '最新价': qt[3],
        '昨收': qt[4],
        '今开': qt[5],
        '成交量': qt[6],
        '成交额': qt[7],
        '最高': qt[22] if len(qt) > 22 else '',
        '最低': qt[21] if len(qt) > 21 else '',
        '涨跌额': qt[47] if len(qt) > 47 else '',
        '涨跌幅': qt[46] if len(qt) > 46 else '',
    }
    
    return result


def get_spot_all(market: str = "all", source: str = "tx", use_cache: bool = True) -> dict[str, Any]:
    """获取全市场行情"""
    return {"error": "全市场行情接口暂不可用，请使用单股票查询"}


def _fetch_all_tx(market: str = "all"):
    """全市场行情暂不可用"""
    raise NotImplementedError("全市场行情接口暂不可用")
