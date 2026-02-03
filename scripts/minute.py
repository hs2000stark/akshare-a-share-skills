"""分时/分钟数据查询模块。

获取股票分时和分钟级别数据。
支持多数据源：东方财富(em)、新浪(sina)
"""

import json
from typing import Any

import akshare as ak


def get_minute(
    symbol: str,
    period: int = 5,
    source: str = "em",
    adjust: str = "",
) -> dict[str, Any]:
    """
    获取股票分钟级别数据。

    @param symbol: 股票代码，如 000001（6位，不带市场前缀）
    @param period: 分钟周期
        - 1: 1分钟（仅近5日，不复权）
        - 5: 5分钟
        - 15: 15分钟
        - 30: 30分钟
        - 60: 60分钟
    @param source: 数据源
        - "em": 东方财富（默认）
        - "sina": 新浪
    @param adjust: 复权方式（仅东方财富支持）
        - "": 不复权
        - "qfq": 前复权
        - "hfq": 后复权
    @returns: 包含分钟数据的字典
    @raises: 网络或数据源异常时抛出

    返回字段包括：
    - 日期：日期
    - 时间：时间
    - 开盘：开盘价
    - 收盘：收盘价
    - 最高：最高价
    - 最低：最低价
    - 成交量：成交量
    - 成交额：成交额
    - 均价：均价
    """
    if source == "sina":
        # 新浪源
        symbol_with_prefix = f"sh{symbol}" if symbol.startswith("6") else f"sz{symbol}"
        df = ak.stock_zh_a_minute(
            symbol=symbol_with_prefix,
            period=period,
            adjust=adjust,
        )
    else:
        # 默认东方财富
        df = ak.stock_zh_a_hist_min_em(
            symbol=symbol,
            period=period,
            adjust=adjust,
        )

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "source": source,
        "period": period,
        "adjust": adjust,
        "count": len(records),
        "data": records,
    }


def get_intraday(symbol: str, source: str = "em") -> dict[str, Any]:
    """
    获取股票日内分时数据。

    @param symbol: 股票代码，如 000001（6位，不带市场前缀）
    @param source: 数据源
        - "em": 东方财富（默认）
        - "sina": 新浪
    @returns: 包含日内分时数据的字典
    @raises: 网络或数据源异常时抛出
    """
    if source == "sina":
        # 新浪源
        symbol_with_prefix = f"sh{symbol}" if symbol.startswith("6") else f"sz{symbol}"
        df = ak.stock_intraday_sina(symbol=symbol_with_prefix)
    else:
        # 默认东方财富
        df = ak.stock_intraday_em(symbol=symbol)

    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "symbol": symbol,
        "source": source,
        "count": len(records),
        "data": records,
    }


def main() -> None:
    """CLI 入口."""
    import argparse

    parser = argparse.ArgumentParser(description="获取分时/分钟数据")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # minute 子命令
    minute_parser = subparsers.add_parser("minute", help="获取分钟数据")
    minute_parser.add_argument("--symbol", required=True, help="股票代码（6位）")
    minute_parser.add_argument(
        "--period",
        type=int,
        choices=[1, 5, 15, 30, 60],
        default=5,
        help="分钟周期",
    )
    minute_parser.add_argument(
        "--source",
        choices=["em", "sina"],
        default="em",
        help="数据源",
    )
    minute_parser.add_argument(
        "--adjust",
        choices=["", "qfq", "hfq"],
        default="",
        help="复权方式",
    )

    # intraday 子命令
    intraday_parser = subparsers.add_parser("intraday", help="获取日内分时数据")
    intraday_parser.add_argument("--symbol", required=True, help="股票代码（6位）")
    intraday_parser.add_argument(
        "--source",
        choices=["em", "sina"],
        default="em",
        help="数据源",
    )

    # 兼容旧参数格式
    parser.add_argument("--symbol", help="股票代码（6位）")
    parser.add_argument(
        "--period", type=int, choices=[1, 5, 15, 30, 60], default=5, help="分钟周期"
    )
    parser.add_argument(
        "--source",
        choices=["em", "sina"],
        default="em",
        help="数据源",
    )
    parser.add_argument(
        "--format",
        choices=["json", "dict"],
        default="json",
        help="输出格式",
    )

    args = parser.parse_args()

    if args.command == "minute":
        result = get_minute(args.symbol, args.period, args.source, args.adjust)
    elif args.command == "intraday":
        result = get_intraday(args.symbol, args.source)
    elif args.symbol:
        # 默认作为 minute 处理
        result = get_minute(args.symbol, args.period, args.source, args.adjust)
    else:
        parser.print_help()
        return

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
