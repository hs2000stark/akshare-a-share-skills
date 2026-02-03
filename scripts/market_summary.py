"""市场总貌查询模块。

查询上交所和深交所的整体市场数据。
接口: stock_sse_summary, stock_szse_summary
"""

import json
from typing import Any

import akshare as ak


def get_sse_summary() -> dict[str, Any]:
    """
    获取上海证券交易所市场总貌数据。

    @returns: 包含上交所总貌数据的字典
    @raises: 网络或数据源异常时抛出

    返回字段包括：
    - 项目：统计项目（流通股本、总市值、平均市盈率、上市公司、上市股票、流通市值、报告时间、总股本）
    - 股票：全部股票合计
    - 科创板：科创板数据
    - 主板：主板数据
    """
    df = ak.stock_sse_summary()

    # 转换为字典格式
    result = {}
    for _, row in df.iterrows():
        item = str(row.get("项目", ""))
        data = {
            "股票": row.get("股票", None),
            "科创板": row.get("科创板", None),
            "主板": row.get("主板", None),
        }
        result[item] = data

    return {
        "market": "sse",
        "name": "上海证券交易所",
        "data": result,
        "raw": json.loads(df.to_json(orient="records", force_ascii=False)),
    }


def get_szse_summary(date: str | None = None) -> dict[str, Any]:
    """
    获取深圳证券交易所市场总貌数据。

    @param date: 查询日期，YYYYMMDD 格式，默认返回最近交易日
    @returns: 包含深交所总貌数据的字典
    @raises: 网络或数据源异常时抛出

    返回字段包括：
    - 证券类别：股票、主板A股、主板B股、中小板、创业板、基金、ETF、LOF、债券等
    - 数量：证券数量（只）
    - 成交金额：成交金额（元）
    - 总市值：总市值（元）
    - 流通市值：流通市值（元）
    """
    if date:
        df = ak.stock_szse_summary(date=date)
    else:
        df = ak.stock_szse_summary()

    # 转换为字典列表
    records = json.loads(df.to_json(orient="records", force_ascii=False))

    return {
        "market": "szse",
        "name": "深圳证券交易所",
        "date": date,
        "count": len(records),
        "data": records,
    }


def main() -> None:
    """CLI 入口."""
    import argparse

    parser = argparse.ArgumentParser(description="获取市场总貌数据")
    parser.add_argument(
        "--market",
        required=True,
        choices=["sse", "szse"],
        help="市场类型：sse=上海证券交易所，szse=深圳证券交易所",
    )
    parser.add_argument(
        "--date", default=None, help="查询日期（YYYYMMDD），仅 szse 支持"
    )
    parser.add_argument(
        "--format",
        choices=["json", "dict"],
        default="json",
        help="输出格式",
    )

    args = parser.parse_args()

    if args.market == "sse":
        result = get_sse_summary()
    else:
        result = get_szse_summary(args.date)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
