"""A股数据查询CLI - 简化版"""

import argparse
import json
import logging
import sys
from . import spot, hist, stock_info as info, macro as macro_mod, news

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def cmd_spot(args):
    """查询实时行情"""
    use_cache = not getattr(args, "no_cache", False)
    return spot.get_spot(args.symbol, use_cache)


def cmd_hist(args):
    """查询历史K线"""
    use_cache = not getattr(args, "no_cache", False)
    return hist.get_hist(args.symbol, args.start, args.end, args.adjust, use_cache)


def cmd_info(args):
    """查询个股信息"""
    use_cache = not getattr(args, "no_cache", False)
    return info.get_stock_info(args.symbol, use_cache)


def cmd_index(args):
    """查询大盘指数"""
    use_cache = not getattr(args, "no_cache", False)
    return macro_mod.get_index_daily(args.symbol, use_cache)


def cmd_news(args):
    """查询财经资讯"""
    use_cache = not getattr(args, "no_cache", False)
    return news.get_stock_news(
        symbol=args.symbol,
        news_type=args.type,
        limit=args.limit or 10,
        use_cache=use_cache
    )


def main():
    parser = argparse.ArgumentParser(description="A股数据查询")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # spot 命令
    spot_parser = subparsers.add_parser("spot", help="实时行情")
    spot_parser.add_argument("--symbol", required=True, help="股票代码")
    spot_parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    spot_parser.set_defaults(func=cmd_spot)

    # hist 命令
    hist_parser = subparsers.add_parser("hist", help="历史K线")
    hist_parser.add_argument("--symbol", required=True, help="股票代码")
    hist_parser.add_argument("--start", required=True, help="开始日期 YYYYMMDD")
    hist_parser.add_argument("--end", required=True, help="结束日期 YYYYMMDD")
    hist_parser.add_argument("--adjust", default="qfq", help="复权类型: qfq/hfq/none")
    hist_parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    hist_parser.set_defaults(func=cmd_hist)

    # info 命令
    info_parser = subparsers.add_parser("info", help="个股信息")
    info_parser.add_argument("--symbol", required=True, help="股票代码")
    info_parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    info_parser.set_defaults(func=cmd_info)

    # index 命令
    index_parser = subparsers.add_parser("index", help="大盘指数")
    index_parser.add_argument("--symbol", required=True, help="指数代码")
    index_parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    index_parser.set_defaults(func=cmd_index)

    # news 命令
    news_parser = subparsers.add_parser("news", help="财经资讯")
    news_parser.add_argument("--symbol", help="股票代码（用于个股新闻）")
    news_parser.add_argument("--type", default="market", 
        choices=["stock", "market", "cls", "breakfast", "global", "sina", "futu", "ths"],
        help="资讯类型: stock-个股新闻, market-全市场新闻, cls-财联社电报, breakfast-财经早餐, global-全球快讯(东财), sina-全球快讯(新浪), futu-富途快讯, ths-同花顺直播")
    news_parser.add_argument("--limit", type=int, default=10, help="返回数量")
    news_parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    news_parser.set_defaults(func=cmd_news)

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    try:
        result = args.func(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
