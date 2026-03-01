# 📈 akshare-a-share

A 股数据查询工具，基于 AKShare 数据源，支持实时行情、历史 K 线、基本面信息、大盘指数、财经资讯等功能。

## 功能特性

- ✅ **实时行情** - 腾讯数据源
- ✅ **历史K线** - 支持日/周/月，复权方式可选
- ✅ **个股信息** - 东方财富网页数据
- ✅ **大盘指数** - 上证/深证指数
- ✅ **财经资讯** - 支持多种资讯类型（市场新闻、财联社、财经早餐、同花顺等）
- ✅ **市场总貌** - 上交所/深交所整体数据
- ✅ **分钟级数据** - 5分钟/15分钟/30分钟/60分钟K线
- ✅ **分时数据** - 日内分时走势

## 快速开始

### 安装依赖

```bash
cd akshare-a-share
uv sync
```

### 使用 CLI

```bash
# 实时行情
uv run python -m scripts.cli spot --symbol 600000

# 历史K线
uv run python -m scripts.cli hist --symbol 600000 --start 20250101 --end 20250227

# 个股信息
uv run python -m scripts.cli info --symbol 600000

# 大盘指数
uv run python -m scripts.cli index --symbol 000001

# 财经资讯
uv run python -m scripts.cli news --type market --limit 10
```

## 接口状态

### CLI 接口（已测试可用）

| 命令 | 功能 |
|------|------|
| `spot --symbol <code>` | 实时行情 |
| `hist --symbol <code> --start <date> --end <date>` | 历史K线 |
| `info --symbol <code>` | 个股信息 |
| `index --symbol <code>` | 大盘指数 |
| `news --type <type> --limit <n>` | 财经资讯 |

### Python 模块

```python
from scripts import market_summary, minute, technical

# 市场总貌
sse = market_summary.get_sse_summary()
szse = market_summary.get_szse_summary()

# 分钟K线
data = minute.get_minute('000001', period=5)

# 分时数据
intraday = technical.get_intraday('000001')
```

## News 类型

- `stock` - 个股新闻
- `market` - 全市场新闻
- `cls` - 财联社电报
- `breakfast` - 财经早餐
- `global` - 全球快讯（东财）
- `sina` - 全球快讯（新浪）
- `futu` - 富途快讯
- `ths` - 同花顺直播

## 注意事项

- 部分接口可能需要代理才能访问
- 如有代理，设置 `http_proxy` 和 `https_proxy` 环境变量
- 请合理请求频率，避免被封禁
