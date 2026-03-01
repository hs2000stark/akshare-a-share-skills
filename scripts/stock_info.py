"""个股基本信息查询模块 - 东财网页接口"""

import json
import logging
from typing import Any

from . import rate_limiter

logger = logging.getLogger(__name__)


def get_stock_info(
    symbol: str,
    source: str = "em",
    timeout: float = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """获取个股基本信息"""
    if use_cache:
        cache_key = f"info_{symbol}_{source}"
        cached = rate_limiter.get_cache().get(cache_key)
        if cached:
            return cached

    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        return _fetch_info(symbol)

    try:
        result = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        raise

    output = {
        "symbol": symbol,
        "source": "em",
        "info": result,
    }

    if use_cache:
        cache = rate_limiter.get_cache()
        cache.ttl_seconds = 3600
        cache.set(cache_key, output)

    return output


def _fetch_info(symbol: str) -> dict[str, Any]:
    """使用东财网页API获取个股信息"""
    import requests
    
    if symbol.startswith('6'):
        market_code = f"SH{symbol}"
    elif symbol.startswith('0') or symbol.startswith('3'):
        market_code = f"SZ{symbol}"
    else:
        market_code = f"SH{symbol}"
    
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax?code={market_code}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://emweb.securities.eastmoney.com/",
    }
    
    resp = requests.get(url, headers=headers, timeout=15)
    data = resp.json()
    
    if 'jbzl' not in data or not data['jbzl']:
        raise ValueError(f"无法获取 {symbol} 的基本信息")
    
    info = data['jbzl'][0]
    
    result = {
        '股票代码': info.get('SECURITY_CODE', ''),
        '股票简称': info.get('SECURITY_NAME_ABBR', ''),
        '公司名称': info.get('ORG_NAME', ''),
        '上市日期': info.get('LISTING_DATE', ''),
        '股票类型': info.get('SECURITY_TYPE', ''),
        '行业': info.get('EM2016', ''),
        '总股本': info.get('REG_CAPITAL', ''),
        '省份': info.get('PROVINCE', ''),
        '城市': info.get('ADDRESS', ''),
        '公司简介': (info.get('ORG_PROFILE', '') or '')[:500],
    }
    
    return result
