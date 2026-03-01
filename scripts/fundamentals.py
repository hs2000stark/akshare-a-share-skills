"""基本面类数据查询模块。

提供财务指标、业绩预告、分红配送、股东数据、估值等基本面数据。
"""

import json
import logging
from typing import Any

import akshare as ak

from . import rate_limiter

logger = logging.getLogger(__name__)


def get_financial_abstract(symbol: str) -> dict[str, Any]:
    """
    获取财务摘要。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 财务摘要数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_financial_abstract_ths(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取财务摘要失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "financial_abstract",
        "count": len(records),
        "data": records,
    }


def get_financial_indicator(symbol: str) -> dict[str, Any]:
    """
    获取财务分析指标。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 财务分析指标数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_financial_analysis_indicator_em(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取财务指标失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "financial_indicator",
        "count": len(records),
        "data": records,
    }


def get_balance_sheet(symbol: str, limit: int = 5) -> dict[str, Any]:
    """
    获取资产负债表。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量，默认最近 5 期
    @returns: 资产负债表数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_zcfz_em(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取资产负债表失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "balance_sheet",
        "count": len(records),
        "data": records,
    }


def get_income_statement(symbol: str, limit: int = 5) -> dict[str, Any]:
    """
    获取利润表。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量，默认最近 5 期
    @returns: 利润表数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_lrb_em(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取利润表失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "income_statement",
        "count": len(records),
        "data": records,
    }


def get_cash_flow(symbol: str, limit: int = 5) -> dict[str, Any]:
    """
    获取现金流量表。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量，默认最近 5 期
    @returns: 现金流量表数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_xjll_em(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取现金流量表失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "cash_flow",
        "count": len(records),
        "data": records,
    }


def get_performance_forecast(symbol: str, limit: int = 5) -> dict[str, Any]:
    """
    获取业绩预告。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量，默认最近 5 条
    @returns: 业绩预告数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_yjbb_em(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取业绩预告失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "performance_forecast",
        "count": len(records),
        "data": records,
    }


def get_dividend(symbol: str, limit: int = 10) -> dict[str, Any]:
    """
    获取分红配送数据。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量，默认最近 10 条
    @returns: 分红配送数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_fhps_em(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取分红数据失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "dividend",
        "count": len(records),
        "data": records,
    }


def get_shareholders(symbol: str) -> dict[str, Any]:
    """
    获取十大流通股东。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 十大流通股东数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_zh_a_gdhs(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取股东数据失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "shareholders",
        "count": len(records),
        "data": records,
    }


def get_shareholder_count(symbol: str) -> dict[str, Any]:
    """
    获取股东户数。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 股东户数数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_zh_a_gdhs(symbol=symbol)
        # 股东户数通常在第一行
        return df.head(10)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取股东户数失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "shareholder_count",
        "count": len(records),
        "data": records,
    }


def get_fund_hold(symbol: str, limit: int = 10) -> dict[str, Any]:
    """
    获取基金持仓。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量，默认最近 10 条
    @returns: 基金持仓数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_report_fund_hold(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取基金持仓失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "fund_hold",
        "count": len(records),
        "data": records,
    }


def get_margin(symbol: str) -> dict[str, Any]:
    """
    获取融资融券数据。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 融资融券数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_margin_sse(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取融资融券失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "margin",
        "count": len(records),
        "data": records,
    }


def get_restricted_shares(symbol: str, limit: int = 10) -> dict[str, Any]:
    """
    获取限售解禁数据。

    @param symbol: 股票代码（6位，不带市场前缀）
    @param limit: 返回数量，默认最近 10 条
    @returns: 限售解禁数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        df = ak.stock_restricted_release_summary_em(symbol=symbol)
        return df.head(limit)

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取限售解禁失败: {e}")
        raise

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "type": "restricted_shares",
        "count": len(records),
        "data": records,
    }


def get_valuation(symbol: str) -> dict[str, Any]:
    """
    获取估值数据（市盈率、市净率等）。

    @param symbol: 股票代码（6位，不带市场前缀）
    @returns: 估值数据
    """
    rate_limiter.get_rate_limiter().wait()

    def _fetch():
        # 获取个股信息，里面包含 PE、PB
        df = ak.stock_individual_info_em(symbol=symbol)
        return df

    try:
        df = rate_limiter.get_retry_handler().execute(_fetch)
    except Exception as e:
        logger.error(f"获取估值数据失败: {e}")
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
        "type": "valuation",
        "data": result,
    }
