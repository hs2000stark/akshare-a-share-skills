"""实时行情查询模块。

查询股票实时行情报价和全市场行情列表。
支持多数据源：东方财富(em)、新浪(sina)
"""

import json
from typing import Any

import akshare as ak


def get_spot(symbol: str, source: str = "em") -> dict[str, Any]:
    """
    获取指定股票的实时五档盘口和报价。

    @param symbol: 股票代码，如 000001（6位，不带市场前缀）
    @param source: 数据源
        - "em": 东方财富（默认，含五档盘口）
        - "sina": 新浪（简洁报价）
    @returns: 包含实时报价的字典
    @raises: 网络或数据源异常时抛出

    东方财富返回字段包括：
    - 最新：最新价
    - 均价：均价
    - 涨幅：涨跌幅（%）
    - 涨跌：涨跌额
    - 总手：成交量（手）
    - 金额：成交额（元）
    - 换手：换手率（%）
    - 量比：量比
    - 最高/最低/今开/昨收
    - 涨停/跌停
    - 外盘/内盘
    - sell_1~5 / buy_1~5：五档卖价/买价及对应成交量

    新浪返回字段包括：
    - 最新价
    - 涨跌额
    - 涨跌幅
    - 买入/卖出
    - 昨收/今开/最高/最低
    - 成交量/成交额
    - 时间戳
    """
    if source == "sina":
        # 新浪需要带市场前缀
        symbol_with_prefix = f"sh{symbol}" if symbol.startswith("6") else f"sz{symbol}"
        df = ak.stock_individual_spot_xq(symbol=symbol_with_prefix)
        # 雪球的格式是 item/value，转为扁平
        result = {}
        for _, row in df.iterrows():
            item = str(row.get("item", ""))
            value = row.get("value", None)
            if value != value:
                value = None
            result[item] = value
    else:
        # 默认东方财富
        df = ak.stock_bid_ask_em(symbol=symbol)
        result = {}
        for _, row in df.iterrows():
            item = str(row.get("item", ""))
            value = row.get("value", None)
            if value != value:
                value = None
            result[item] = value

    return {
        "symbol": symbol,
        "source": source,
        "quote": result,
        "raw": json.loads(df.to_json(orient="records", force_ascii=False)),
    }


def get_spot_all(market: str = "all", source: str = "em") -> dict[str, Any]:
    """
    获取全市场或指定市场的实时行情列表。

    @param market: 市场类型
        - "all": 沪深京 A 股（默认）
        - "sh": 上海 A 股
        - "sz": 深圳 A 股
        - "bj": 北京 A 股
    @param source: 数据源
        - "em": 东方财富（默认，数据更全面）
        - "sina": 新浪
    @returns: 包含全市场行情的字典
    @raises: 网络或数据源异常时抛出

    返回字段包括：
    - 序号：序号
    - 代码：股票代码
    - 名称：股票名称
    - 最新价：最新成交价
    - 涨跌幅：涨跌幅（%）
    - 涨跌额：涨跌额
    - 成交量：成交量（手）
    - 成交额：成交额（元）
    - 振幅：振幅（%）
    - 最高/最低/今开/昨收
    - 量比：量比
    - 换手率：换手率（%）
    - 市盈率-动态：PE
    - 市净率：PB
    - 总市值：总市值（元）
    - 流通市值：流通市值（元）
    - 涨速：涨速
    - 5分钟涨跌：5分钟涨跌幅（%）
    - 60日涨跌幅：60日涨跌幅（%）
    - 年初至今涨跌幅：年初至今涨跌幅（%）
    """
    if source == "sina":
        # 新浪源
        df = ak.stock_zh_a_spot()
    else:
        # 默认东方财富
        if market == "all":
            df = ak.stock_zh_a_spot_em()
        elif market == "sh":
            df = ak.stock_sh_a_spot_em()
        elif market == "sz":
            df = ak.stock_sz_a_spot_em()
        elif market == "bj":
            df = ak.stock_bj_a_spot_em()
        else:
            raise ValueError(f"不支持的市场类型: {market}")

    # 转换为字典列表
    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "market": market,
        "source": source,
        "count": len(records),
        "data": records,
    }


def main() -> None:
    """CLI 入口."""
    import argparse

    parser = argparse.ArgumentParser(description="获取实时行情")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 单只股票行情
    spot_parser = subparsers.add_parser("symbol", help="查询单只股票行情")
    spot_parser.add_argument("--symbol", required=True, help="股票代码（6位）")
    spot_parser.add_argument(
        "--source",
        choices=["em", "sina"],
        default="em",
        help="数据源",
    )

    # 全市场行情
    all_parser = subparsers.add_parser("all", help="查询全市场行情")
    all_parser.add_argument(
        "--market",
        choices=["all", "sh", "sz", "bj"],
        default="all",
        help="市场类型",
    )
    all_parser.add_argument(
        "--source",
        choices=["em", "sina"],
        default="em",
        help="数据源",
    )

    # 兼容旧参数格式
    parser.add_argument("--symbol", help="股票代码（6位）")
    parser.add_argument(
        "--source",
        choices=["em", "sina"],
        default="em",
        help="数据源",
    )
    parser.add_argument(
        "--all", action="store_true", help="获取全市场行情"
    )
    parser.add_argument(
        "--market",
        choices=["all", "sh", "sz", "bj"],
        default="all",
        help="市场类型",
    )
    parser.add_argument(
        "--format",
        choices=["json", "dict"],
        default="json",
        help="输出格式",
    )

    args = parser.parse_args()

    if args.all or (not args.symbol and args.command == "all"):
        # 全市场
        result = get_spot_all(args.market, args.source)
    elif args.symbol:
        # 单只股票
        result = get_spot(args.symbol, args.source)
    elif args.command == "symbol":
        result = get_spot(args.symbol, args.source)
    elif args.command == "all":
        result = get_spot_all(args.market, args.source)
    else:
        parser.print_help()
        return

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
