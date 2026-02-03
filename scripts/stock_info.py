"""个股信息查询模块。

查询股票的基本信息：总市值、行业、上市时间、股本等。
支持多数据源：东方财富(em)、雪球(xq)
"""

import json
from typing import Any

import akshare as ak


def get_stock_info(symbol: str, source: str = "em", timeout: float | None = None) -> dict[str, Any]:
    """
    获取指定股票的详细信息。

    @param symbol: 股票代码，如 000001、603777（6位，不带市场前缀）
    @param source: 数据源
        - "em": 东方财富（默认）
        - "xq": 雪球
    @param timeout: 超时时间（秒），默认 None
    @returns: 包含个股信息的字典
    @raises: 网络或数据源异常时抛出

    返回字段包括：
    - 最新：最新价
    - 股票代码：证券代码
    - 股票简称：股票名称
    - 总股本：总股本（股）
    - 流通股：流通股本（股）
    - 总市值：总市值（元）
    - 流通市值：流通市值（元）
    - 行业：所属行业
    - 上市时间：上市日期（YYYYMMDD）
    """
    if source == "xq":
        # 雪球需要带市场前缀
        symbol_with_prefix = f"SH{symbol}" if symbol.startswith("6") else f"SZ{symbol}"
        df = ak.stock_individual_basic_info_xq(symbol=symbol_with_prefix, timeout=timeout)
    else:
        # 默认东方财富
        df = ak.stock_individual_info_em(symbol=symbol, timeout=timeout)

    # 转换为字典格式，便于 JSON 输出
    result = {}
    for _, row in df.iterrows():
        item = str(row.get("item", ""))
        value = row.get("value", None)
        # 处理 NaN 值
        if value != value:  # NaN check
            value = None
        result[item] = value

    return {
        "symbol": symbol,
        "source": source,
        "info": result,
        "raw": json.loads(df.to_json(orient="records", force_ascii=False)),
    }


def main() -> None:
    """CLI 入口."""
    import argparse

    parser = argparse.ArgumentParser(description="获取个股基本信息")
    parser.add_argument("--symbol", required=True, help="股票代码（6位）")
    parser.add_argument(
        "--source",
        choices=["em", "xq"],
        default="em",
        help="数据源：em=东方财富，xq=雪球",
    )
    parser.add_argument(
        "--timeout", type=float, default=None, help="超时时间（秒）"
    )
    parser.add_argument(
        "--format",
        choices=["json", "dict"],
        default="json",
        help="输出格式",
    )

    args = parser.parse_args()
    result = get_stock_info(args.symbol, args.source, args.timeout)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
