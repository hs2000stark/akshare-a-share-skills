"""历史 K 线查询模块。

获取股票历史行情数据（日/周/月 K 线）。
支持多数据源：东方财富(em)、新浪(sina)、腾讯(tx)
"""

import json
from typing import Any

import akshare as ak


def get_hist(
    symbol: str,
    start_date: str,
    end_date: str,
    period: str = "daily",
    adjust: str = "",
    source: str = "em",
) -> dict[str, Any]:
    """
    获取 A 股历史日/周/月 K 线。

    @param symbol: 股票代码，如 000001、603777（6位，不带市场前缀）
    @param start_date: 开始日期，YYYYMMDD 格式
    @param end_date: 结束日期，YYYYMMDD 格式
    @param period: K线周期
        - "daily": 日 K 线（默认）
        - "weekly": 周 K 线
        - "monthly": 月 K 线
    @param adjust: 复权方式
        - "": 不复权（默认）
        - "qfq": 前复权
        - "hfq": 后复权
    @param source: 数据源
        - "em": 东方财富（默认，数据最全面）
        - "sina": 新浪
        - "tx": 腾讯
    @returns: 包含历史 K 线数据的字典
    @raises: 网络或数据源异常时抛出

    返回字段包括：
    - 日期：交易日期
    - 股票代码：证券代码
    - 开盘：开盘价
    - 收盘：收盘价
    - 最高：最高价
    - 最低：最低价
    - 成交量：成交量（手）
    - 成交额：成交额（元）
    - 振幅：振幅（%）
    - 涨跌幅：涨跌幅（%）
    - 涨跌额：涨跌额
    - 换手率：换手率（%）

    复权说明：
    - 不复权：原始价格，存在除权除息缺口
    - 前复权 (qfq)：当前价不变，历史价向前调整，适合看盘
    - 后复权 (hfq)：历史价不变，当前价向后调整，适合量化研究

    数据源差异：
    - 东方财富 (em): 支持日/周/月 K 线，数据最全面
    - 新浪 (sina): 支持日 K 线，注意可能被封 IP
    - 腾讯 (tx): 支持日 K 线，历史数据完整
    """
    if source == "tx":
        # 腾讯需要带市场前缀
        symbol_with_prefix = f"sz{symbol}" if symbol.startswith("0") or symbol.startswith("3") else f"sh{symbol}"
        df = ak.stock_zh_a_hist_tx(
            symbol=symbol_with_prefix,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    elif source == "sina":
        # 新浪需要带市场前缀
        symbol_with_prefix = f"sh{symbol}" if symbol.startswith("6") else f"sz{symbol}"
        df = ak.stock_zh_a_daily(
            symbol=symbol_with_prefix,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    else:
        # 默认东方财富
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )

    # 转换为字典列表
    records = json.loads(df.to_json(orient="records", force_ascii=False))

    # 添加一些统计信息
    if records:
        closes = [r.get("收盘", 0) if "收盘" in r else r.get("close", 0) for r in records]
        if closes:
            first_close = closes[0]
            last_close = closes[-1]
            change_pct = ((last_close - first_close) / first_close * 100) if first_close else 0
            stats = {
                "start_date": records[0].get("日期") or records[0].get("date"),
                "end_date": records[-1].get("日期") or records[-1].get("date"),
                "total_days": len(records),
                "first_close": first_close,
                "last_close": last_close,
                "total_change_pct": round(change_pct, 2),
            }
        else:
            stats = None
    else:
        stats = None

    return {
        "symbol": symbol,
        "source": source,
        "period": period,
        "adjust": adjust,
        "start_date": start_date,
        "end_date": end_date,
        "count": len(records),
        "stats": stats,
        "data": records,
    }


def main() -> None:
    """CLI 入口."""
    import argparse

    parser = argparse.ArgumentParser(description="获取历史 K 线数据")
    parser.add_argument("--symbol", required=True, help="股票代码（6位）")
    parser.add_argument(
        "--start", required=True, help="开始日期（YYYYMMDD）"
    )
    parser.add_argument("--end", required=True, help="结束日期（YYYYMMDD）")
    parser.add_argument(
        "--period",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="K线周期",
    )
    parser.add_argument(
        "--adjust",
        choices=["", "qfq", "hfq"],
        default="",
        help="复权方式",
    )
    parser.add_argument(
        "--source",
        choices=["em", "sina", "tx"],
        default="em",
        help="数据源：em=东方财富，sina=新浪，tx=腾讯",
    )
    parser.add_argument(
        "--format",
        choices=["json", "dict"],
        default="json",
        help="输出格式",
    )

    args = parser.parse_args()
    result = get_hist(
        args.symbol, args.start, args.end, args.period, args.adjust, args.source
    )

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
