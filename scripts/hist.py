"""历史K线查询模块 - 腾讯接口"""

import json
import logging
from typing import Any

from . import rate_limiter

logger = logging.getLogger(__name__)


def get_hist(
    symbol: str,
    start: str,
    end: str,
    period: str = "daily",
    adjust: str = "",
    source: str = "tx",
    use_cache: bool = True,
) -> dict[str, Any]:
    """获取历史K线数据"""
    if use_cache:
        cache_key = f"hist_{symbol}_{start}_{end}_{period}_{adjust}"
        cached = rate_limiter.get_cache().get(cache_key)
        if cached:
            return cached

    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        return _fetch_tx_hist(symbol, start, end, period, adjust)

    try:
        result = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        raise

    output = {
        "symbol": symbol,
        "start": start,
        "end": end,
        "period": period,
        "adjust": adjust,
        "source": "tx",
        "data": result,
    }

    if use_cache:
        cache = rate_limiter.get_cache()
        cache.ttl_seconds = 3600
        cache.set(cache_key, output)

    return output


def _fetch_tx_hist(symbol: str, start: str, end: str, period: str = "daily", adjust: str = "") -> list:
    """使用腾讯接口获取历史K线"""
    import requests
    from datetime import datetime, timedelta
    
    if symbol.startswith('6'):
        market = 'sh'
    elif symbol.startswith('0') or symbol.startswith('3'):
        market = 'sz'
    else:
        market = 'sh'
    
    full_symbol = f"{market}{symbol}"
    
    # 计算需要的天数
    try:
        start_dt = datetime.strptime(start, '%Y%m%d')
        end_dt = datetime.strptime(end, '%Y%m%d')
        days = (end_dt - start_dt).days + 100
    except:
        days = 200
    
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={full_symbol},day,,,{days},qfqa"
    
    resp = requests.get(url, timeout=15)
    data = resp.json()
    
    day_data = data['data'][full_symbol]['day']
    
    result = []
    for item in day_data:
        if isinstance(item, list):
            date_str = item[0].replace('-', '')
            if start <= date_str <= end:
                result.append({
                    '日期': item[0],
                    '开盘': item[1],
                    '收盘': item[2],
                    '最高': item[3],
                    '最低': item[4],
                    '成交量': item[5],
                })
    
    return result
