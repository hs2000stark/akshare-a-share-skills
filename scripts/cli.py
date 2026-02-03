#!/usr/bin/env python3
"""AKShare A 股数据查询 - 统一 CLI 入口。

支持查询：
- info: 个股基本信息 (em/xq)
- spot: 实时行情 (em/sina)
- hist: 历史 K 线 (em/sina/tx)
- minute: 分钟数据 (em/sina)
- intraday: 日内分时 (em/sina)
- summary: 市场总貌
"""

import argparse
import json
import sys


def cmd_info(args: argparse.Namespace) -> dict:
    """查询个股基本信息."""
    from .stock_info import get_stock_info

    return get_stock_info(args.symbol, args.source, args.timeout)


def cmd_spot(args: argparse.Namespace) -> dict:
    """查询实时行情."""
    from .spot import get_spot, get_spot_all

    if args.all or args.market:
        return get_spot_all(args.market or "all", args.source)
    return get_spot(args.symbol, args.source)


def cmd_hist(args: argparse.Namespace) -> dict:
    """查询历史 K 线."""
    from .hist import get_hist

    return get_hist(
        args.symbol, args.start, args.end, args.period, args.adjust, args.source
    )


def cmd_minute(args: argparse.Namespace) -> dict:
    """查询分钟数据."""
    from .minute import get_minute

    return get_minute(args.symbol, args.period, args.source, args.adjust)


def cmd_intraday(args: argparse.Namespace) -> dict:
    """查询日内分时数据."""
    from .minute import get_intraday

    return get_intraday(args.symbol, args.source)


def cmd_summary(args: argparse.Namespace) -> dict:
    """查询市场总貌."""
    from .market_summary import get_sse_summary, get_szse_summary

    if args.market == "sse":
        return get_sse_summary()
    return get_szse_summary(args.date)


def main() -> None:
    """CLI 主入口."""
    parser = argparse.ArgumentParser(
        description="AKShare A 股数据查询工具（多数据源）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
数据源说明:
  em   - 东方财富（默认，数据最全面）
  sina - 新浪财经（注意可能封 IP）
  tx   - 腾讯证券（历史数据为主）
  xq   - 雪球财经（个股信息详细）

示例:
  # 个股基本信息
  %(prog)s info --symbol 000001
  %(prog)s info --symbol 000001 --source xq

  # 实时行情
  %(prog)s spot --symbol 000001
  %(prog)s spot --symbol 000001 --source sina
  %(prog)s spot --all

  # 历史 K 线
  %(prog)s hist --symbol 000001 --start 20230101 --end 20231231 --adjust hfq
  %(prog)s hist --symbol 000001 --start 20230101 --end 20231231 --source tx

  # 分钟数据
  %(prog)s minute --symbol 000001 --period 5
  %(prog)s minute --symbol 000001 --period 1 --source sina

  # 日内分时
  %(prog)s intraday --symbol 000001

  # 市场总貌
  %(prog)s summary --market sse
  %(prog)s summary --market szse --date 20250619
        """,
    )

    parser.add_argument(
        "--format",
        choices=["json", "dict"],
        default="json",
        help="输出格式（默认: json）",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON 缩进（默认: 2）",
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # info 命令
    info_parser = subparsers.add_parser("info", help="查询个股基本信息")
    info_parser.add_argument("--symbol", required=True, help="股票代码（6位）")
    info_parser.add_argument(
        "--source",
        choices=["em", "xq"],
        default="em",
        help="数据源",
    )
    info_parser.add_argument(
        "--timeout", type=float, default=None, help="超时时间（秒）"
    )

    # spot 命令
    spot_parser = subparsers.add_parser("spot", help="查询实时行情")
    spot_group = spot_parser.add_mutually_exclusive_group()
    spot_group.add_argument("--symbol", help="股票代码（6位）")
    spot_group.add_argument(
        "--all", action="store_true", help="获取全市场行情"
    )
    spot_parser.add_argument(
        "--market",
        choices=["all", "sh", "sz", "bj"],
        default="all",
        help="市场类型（与 --all 配合使用）",
    )
    spot_parser.add_argument(
        "--source",
        choices=["em", "sina"],
        default="em",
        help="数据源",
    )

    # hist 命令
    hist_parser = subparsers.add_parser("hist", help="查询历史 K 线")
    hist_parser.add_argument("--symbol", required=True, help="股票代码（6位）")
    hist_parser.add_argument(
        "--start", required=True, help="开始日期（YYYYMMDD）"
    )
    hist_parser.add_argument(
        "--end", required=True, help="结束日期（YYYYMMDD）"
    )
    hist_parser.add_argument(
        "--period",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="K线周期",
    )
    hist_parser.add_argument(
        "--adjust",
        choices=["", "qfq", "hfq"],
        default="",
        help="复权方式",
    )
    hist_parser.add_argument(
        "--source",
        choices=["em", "sina", "tx"],
        default="em",
        help="数据源",
    )

    # minute 命令
    minute_parser = subparsers.add_parser("minute", help="查询分钟数据")
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

    # intraday 命令
    intraday_parser = subparsers.add_parser("intraday", help="查询日内分时数据")
    intraday_parser.add_argument("--symbol", required=True, help="股票代码（6位）")
    intraday_parser.add_argument(
        "--source",
        choices=["em", "sina"],
        default="em",
        help="数据源",
    )

    # summary 命令
    summary_parser = subparsers.add_parser(
        "summary", help="查询市场总貌"
    )
    summary_parser.add_argument(
        "--market",
        required=True,
        choices=["sse", "szse"],
        help="市场类型",
    )
    summary_parser.add_argument(
        "--date", default=None, help="查询日期（YYYYMMDD），仅 szse 支持"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行对应命令
    command_map = {
        "info": cmd_info,
        "spot": cmd_spot,
        "hist": cmd_hist,
        "minute": cmd_minute,
        "intraday": cmd_intraday,
        "summary": cmd_summary,
    }

    try:
        result = command_map[args.command](args)

        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=args.indent))
        else:
            print(result)

    except Exception as e:
        error_result = {
            "error": str(e),
            "command": args.command,
            "args": vars(args),
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
