"""资讯类数据接口 - 支持多种财经资讯"""

import logging
from typing import Any, Optional

from . import rate_limiter

logger = logging.getLogger(__name__)


def get_stock_news(
    symbol: Optional[str] = None,
    news_type: str = "market",
    limit: int = 10,
    use_cache: bool = True
) -> dict[str, Any]:
    """获取各类财经资讯
    
    Args:
        symbol: 股票代码（用于个股新闻）
        news_type: 资讯类型
            - stock: 个股新闻
            - market: 全市场财经新闻
            - cls: 财联社电报
            - breakfast: 财经早餐
            - global: 全球财经快讯(东财)
            - sina: 全球财经快讯(新浪)
            - futu: 富途快讯
            - ths: 同花顺直播
        limit: 返回数量
        use_cache: 是否使用缓存
    """
    cache_key = f"news_{news_type}_{symbol or 'none'}_{limit}"
    
    if use_cache:
        cached = rate_limiter.get_cache().get(cache_key)
        if cached:
            return cached

    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        if news_type == "stock":
            return _fetch_stock_news(symbol, limit)
        elif news_type == "market":
            return _fetch_market_news(limit)
        elif news_type == "cls":
            return _fetch_cls_news(limit)
        elif news_type == "breakfast":
            return _fetch_breakfast(limit)
        elif news_type == "global":
            return _fetch_global_em(limit)
        elif news_type == "sina":
            return _fetch_global_sina(limit)
        elif news_type == "futu":
            return _fetch_global_futu(limit)
        elif news_type == "ths":
            return _fetch_global_ths(limit)
        else:
            raise ValueError(f"Unknown news type: {news_type}")

    try:
        result = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        raise

    output = {
        "type": news_type,
        "symbol": symbol,
        "source": "eastmoney",
        "news": result,
    }

    if use_cache:
        cache = rate_limiter.get_cache()
        cache.ttl_seconds = 1800  # 30分钟
        cache.set(cache_key, output)

    return output


# ========== 个股新闻 ==========
def _fetch_stock_news(symbol: str, limit: int = 10) -> list:
    """获取个股新闻 - akshare stock_news_em"""
    import akshare as ak
    
    df = ak.stock_news_em(symbol=symbol)
    
    result = []
    for _, row in df.head(200).iterrows():
        result.append({
            "title": str(row.get("新闻标题", "")),
            "content": str(row.get("新闻内容", ""))[:200],
            "time": str(row.get("发布时间", "")),
            "source": str(row.get("文章来源", "")),
            "url": str(row.get("新闻链接", "")),
        })
    
    return result


# ========== 全市场财经新闻 ==========
def _fetch_market_news(limit: int = 10) -> list:
    """获取全市场财经新闻 - 东财"""
    import requests
    
    url = f"https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_{limit}_1_.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    resp = requests.get(url, headers=headers, timeout=15)
    text = resp.text
    
    if text.startswith("var ajaxResult="):
        text = text[len("var ajaxResult="):]
    
    import json
    data = json.loads(text)
    
    news_list = data.get("LivesList", [])
    
    result = []
    for item in news_list[:limit]:
        result.append({
            "title": item.get("title", ""),
            "digest": item.get("digest", ""),
            "url": item.get("url_w", ""),
            "time": item.get("showtime", ""),
        })
    
    return result


# ========== 财经早餐 ==========
def _fetch_breakfast(limit: int = 10) -> list:
    """财经早餐 - 默认只获取当天(和最近1-2天)的数据，返回每条新闻解析"""
    import akshare as ak
    from datetime import datetime
    import re
    
    df = ak.stock_info_cjzc_em()
    
    # 获取今天的日期字符串 (格式: 2026-03-02)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 过滤只保留今天发布的数据
    df_today = df[df["发布时间"].astype(str).str.startswith(today)]
    
    # 如果当天没有数据（节假日等情况），则获取最近的数据
    if len(df_today) == 0:
        df_today = df.head(limit)
    else:
        # 只取当天数据，最多limit条
        df_today = df_today.head(limit)
    
    result = []
    for _, row in df_today.iterrows():
        digest = str(row.get("摘要", ""))
        
        # 解析每条新闻
        news_items = _parse_breakfast_items(digest)
        
        result.append({
            "title": str(row.get("标题", "")),
            "digest": digest,
            "time": str(row.get("发布时间", "")),
            "url": str(row.get("链接", "")),
            "items": news_items,  # 解析后的每条新闻
        })
    
    return result


def _parse_breakfast_items(digest: str) -> list:
    """解析财经早餐摘要中的每条新闻"""
    import re
    
    # 去掉开头的标题【...】
    digest_clean = re.sub(r'【[^】]+】', '', digest)
    
    # 按数字+、分割
    news_items = re.split(r'(\d+)、', digest_clean)
    
    items = []
    for i in range(1, len(news_items), 2):
        if i+1 < len(news_items):
            items.append({
                "id": news_items[i],
                "content": news_items[i+1].strip()
            })
    
    return items


# ========== 财联社电报 ==========
def _fetch_cls_news(limit: int = 10) -> list:
    """财联社电报"""
    import akshare as ak
    
    df = ak.stock_info_global_cls(symbol="全部")
    
    result = []
    for _, row in df.head(200).iterrows():
        result.append({
            "title": str(row.get("标题", "")),
            "content": str(row.get("内容", "")),
            "date": str(row.get("发布日期", "")),
            "time": str(row.get("发布时间", "")),
        })
    
    return result


# ========== 全球财经快讯(东财) ==========
def _fetch_global_em(limit: int = 10) -> list:
    """全球财经快讯(东财)"""
    import akshare as ak
    
    df = ak.stock_info_global_em()
    
    result = []
    for _, row in df.head(200).iterrows():
        result.append({
            "title": str(row.get("标题", "")),
            "digest": str(row.get("摘要", "")),
            "time": str(row.get("发布时间", "")),
            "url": str(row.get("链接", "")),
        })
    
    return result


# ========== 全球财经快讯(新浪) ==========
def _fetch_global_sina(limit: int = 10) -> list:
    """全球财经快讯(新浪)"""
    import akshare as ak
    
    df = ak.stock_info_global_sina()
    
    result = []
    for _, row in df.head(200).iterrows():
        result.append({
            "time": str(row.get("时间", "")),
            "content": str(row.get("内容", "")),
        })
    
    return result


# ========== 富途快讯 ==========
def _fetch_global_futu(limit: int = 10) -> list:
    """富途快讯"""
    import akshare as ak
    
    df = ak.stock_info_global_futu()
    
    result = []
    for _, row in df.head(200).iterrows():
        result.append({
            "title": str(row.get("标题", "")),
            "content": str(row.get("内容", "")),
            "time": str(row.get("发布时间", "")),
            "url": str(row.get("链接", "")),
        })
    
    return result


# ========== 同花顺直播 ==========
def _fetch_global_ths(limit: int = 10) -> list:
    """同花顺直播"""
    import akshare as ak
    
    df = ak.stock_info_global_ths()
    
    result = []
    for _, row in df.head(200).iterrows():
        result.append({
            "title": str(row.get("标题", "")),
            "content": str(row.get("内容", "")),
            "time": str(row.get("发布时间", "")),
            "url": str(row.get("链接", "")),
        })
    
    return result


# ========== 财经早餐详情抓取 ==========
def fetch_breakfast_detail(url: str) -> dict:
    """抓取财经早餐链接的详细内容"""
    import requests
    from bs4 import BeautifulSoup
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 获取标题
        title = soup.find('title')
        title = title.text if title else ""
        
        # 获取所有段落文本
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4'])
        
        content_text = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 10:
                content_text.append(text)
        
        return {
            "title": title,
            "content": content_text,
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
