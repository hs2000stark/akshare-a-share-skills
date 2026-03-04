"""历史K线查询模块 - 腾讯财经接口"""

import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


def get_hist(
    symbol: str,
    start: str,
    end: str,
    period: str = "daily",
    adjust: str = "",
    source: str = "eastmoney",
    use_cache: bool = True,
) -> dict[str, Any]:
    """获取历史K线数据
    source: eastmoney (东财) 或 tencent (腾讯财经)
    """
    # 简单的内存缓存
    cache_key = f"hist_{symbol}_{start}_{end}_{period}_{adjust}_{source}"
    if use_cache and hasattr(get_hist, '_cache'):
        if cache_key in get_hist._cache:
            return get_hist._cache[cache_key]
    
    # 添加短暂延迟，避免请求过快
    time.sleep(0.5)
    
    result = _fetch_tx_hist(symbol, start, end, period, adjust)
    
    output = {
        "symbol": symbol,
        "start": start,
        "end": end,
        "period": period,
        "adjust": adjust,
        "source": "tencent",
        "data": result,
    }
    
    if use_cache:
        if not hasattr(get_hist, '_cache'):
            get_hist._cache = {}
        get_hist._cache[cache_key] = output
    
    return output


def _fetch_tx_hist(symbol: str, start: str, end: str, period: str = "daily", adjust: str = "") -> list:
    """使用腾讯财经接口获取历史K线 (akshare)"""
    import akshare as ak
    
    # 转换日期格式
    start_date = f"{start[:4]}-{start[4:6]}-{start[6:]}"
    end_date = f"{end[:4]}-{end[4:6]}-{end[6:]}"
    
    # 添加市场前缀
    if symbol.startswith('6'):
        market = 'sh'
    elif symbol.startswith('0') or symbol.startswith('3'):
        market = 'sz'
    elif symbol.startswith('8') or symbol.startswith('4'):
        market = 'bj'
    else:
        market = 'sh'
    
    full_symbol = f"{market}{symbol}"
    
    # 复权类型转换
    adjust_map = {"qfq": "qfq", "hfq": "hfq", "none": ""}
    adjust_type = adjust_map.get(adjust, "qfq")
    
    df = ak.stock_zh_a_hist_tx(
        symbol=full_symbol,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust_type
    )
    
    result = []
    for _, row in df.iterrows():
        result.append({
            '日期': str(row['date']),
            '开盘': float(row['open']),
            '收盘': float(row['close']),
            '最高': float(row['high']),
            '最低': float(row['low']),
            '成交量': float(row['amount']) if row['amount'] else 0,
        })
    
    return result
