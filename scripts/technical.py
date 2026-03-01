"""技术行情类数据查询模块。

提供分时数据、分钟K线、筹码分布、龙虎榜等技术分析数据。
"""

import json
import logging
from typing import Any

import akshare as ak

from . import rate_limiter

logger = logging.getLogger(__name__)


def get_intraday(symbol: str, source: str = "em") -> dict[str, Any]:
    """
    获取日内分时数据。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param source: 数据源，em（东方财富）或 sina（新浪）
    @returns: 分时数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        if source == "sina":
            df = ak.stock_intraday_sina(symbol=symbol)
        else:
            df = ak.stock_intraday_em(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取分时数据失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "source": source,
        "type": "intraday",
        "count": len(records),
        "data": records,
    }


def get_minute(symbol: str, period: int = 5, adjust: str = "") -> dict[str, Any]:
    """
    获取分钟K线数据。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param period: 分钟周期，1/5/15/30/60
    @param adjust: 复权方式
    @returns: 分钟K线数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_zh_a_hist_min_em(
            symbol=symbol,
            period=f"{period}",
            adjust=adjust,
        )
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取分钟K线失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "period": period,
        "type": "minute",
        "count": len(records),
        "data": records,
    }


def get_tick_data(symbol: str, date: str | None = None) -> dict[str, Any]:
    """
    获取分笔数据（逐笔成交）。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param date: 日期（YYYYMMDD），默认最新交易日
    @returns: 分笔数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_zh_a_tick_tx_js(symbol=symbol, date=date)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取分笔数据失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "date": date,
        "type": "tick",
        "count": len(records),
        "data": records,
    }


def get_individual_fund_flow(symbol: str) -> dict[str, Any]:
    """
    获取个股资金流向。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 资金流向数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_individual_fund_flow(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取资金流向失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "fund_flow",
        "count": len(records),
        "data": records,
    }


def get_chip_distribution(symbol: str) -> dict[str, Any]:
    """
    获取筹码分布。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 筹码分布数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_cyq_em(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取筹码分布失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "chip",
        "count": len(records),
        "data": records,
    }


def get_lhb_detail(date: str | None = None) -> dict[str, Any]:
    """
    获取龙虎榜详情。

    @param date: 日期（YYYYMMDD），默认最新交易日
    @returns: 龙虎榜详情数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_lhb_detail_em(date=date)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取龙虎榜失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "date": date,
        "type": "lhb_detail",
        "count": len(records),
        "data": records,
    }


def get_lhb_stock(symbol: str, limit: int = 10) -> dict[str, Any]:
    """
    获取龙虎榜个股详情。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量
    @returns: 龙虎榜个股数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_lhb_stock_detail_em(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取龙虎榜个股失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "lhb_stock",
        "count": len(records),
        "data": records,
    }


def get_zt_pool(date: str | None = None) -> dict[str, Any]:
    """
    获取涨停板行情。

    @param date: 日期（YYYYMMDD），默认最新交易日
    @returns: 涨停板数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_zt_pool_em(date=date)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取涨停板失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "date": date,
        "type": "zt_pool",
        "count": len(records),
        "data": records,
    }


def get_zt_pool_strong(limit: int = 20) -> dict[str, Any]:
    """
    获取强势股池。

    @param limit: 返回数量
    @returns: 强势股数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_zt_pool_strong_em(limit=limit)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取强势股失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "type": "zt_pool_strong",
        "count": len(records),
        "data": records,
    }


def get_stock_bid_ask(symbol: str) -> dict[str, Any]:
    """
    获取五档盘口数据。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 五档盘口数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_bid_ask_em(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取五档盘口失败: {e}")
        raise

    # 转换为字典
    result = {}
    for _, row in df.iterrows():
        item = str(row.get("item", ""))
        value = row.get("value", None)
        if value != value:  # NaN check
            value = None
        result[item] = value

    return {
        "symbol": symbol,
        "type": "bid_ask",
        "data": result,
    }


def get_fund_flow_big_deal(symbol: str, limit: int = 20) -> dict[str, Any]:
    """
    获取大单交易数据。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量
    @returns: 大单交易数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_fund_flow_big_deal(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取大单交易失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "big_deal",
        "count": len(records),
        "data": records,
    }
