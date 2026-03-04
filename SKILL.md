---
name: akshare-a-share
description: "查询 A 股实时行情、历史 K 线、个股信息、大盘指数与财经新闻（支持多数据源：腾讯/新浪/东财）。"
metadata: {"openclaw":{"emoji":"📈","requires":{"bins":["uv","python"],"pip":["akshare","pandas","requests"]}}}
---

# AKShare A 股数据查询

当用户需要查询以下信息时使用本 skill：
- 个股实时行情（最新价、涨跌幅）
- 历史 K 线（日/周/月，支持复权）
- 个股基本信息（市值、行业、简介）
- 大盘指数行情（上证、深证）
- 个股财经新闻
- 市场总貌（上交所/深交所）
- 分钟级/分时数据

## 前置条件

```bash
cd akshare-a-share
uv sync  # 安装依赖
```

## 可用接口列表

### ✅ CLI 已暴露接口

| 类别 | 功能 | 命令 | 数据源 | 状态 |
|------|------|------|--------|------|
| 技术行情 | 实时行情 | `spot --symbol 600000` | 腾讯 | ✅ 可用 |
| 技术行情 | 历史K线 | `hist --symbol 600000 --start 20250101 --end 20250227` | 腾讯 | ✅ 可用 |
| 基本面 | 个股信息 | `info --symbol 600000` | 东财网页 | ✅ 可用 |
| 宏观类 | 大盘指数 | `index --symbol 000001` | 腾讯 | ✅ 可用 |
| 资讯类 | 个股新闻 | `news --symbol 600000 --type stock` | 新浪 | ✅ 可用 |
| 资讯类 | 市场新闻 | `news --type market --limit 100` | 东财 | ✅ 可用 |
| 资讯类 | 财联社电报 | `news --type cls --limit 100` | 财联社 | ✅ 可用 |
| 资讯类 | 财经早餐 | `news --type breakfast --limit 100` | 东财 | ✅ 可用 |
| 资讯类 | 全球快讯(东财) | `news --type global --limit 100` | 东财 | ✅ 可用 |
| 资讯类 | 全球快讯(新浪) | `news --type sina --limit 100` | 新浪 | ✅ 可用 |
| 资讯类 | 富途快讯 | `news --type futu --limit 100` | 富途 | ✅ 可用 |
| 资讯类 | 同花顺直播 | `news --type ths --limit 100` | 同花顺 | ✅ 可用 |

### ✅ Python 模块可用接口（未暴露 CLI）

| 类别 | 功能 | 调用方式 | 数据源 | 状态 |
|------|------|----------|--------|------|
| 市场总貌 | 上交所总貌 | `market_summary.get_sse_summary()` | 东财 | ✅ 可用 |
| 市场总貌 | 深交所总貌 | `market_summary.get_szse_summary()` | 东财 | ✅ 可用 |
| 分钟数据 | 分钟K线 | `minute.get_minute(symbol, period=5)` | 东财 | ✅ 可用 |
| 技术行情 | 分时数据 | `technical.get_intraday(symbol)` | 东财/新浪 | ✅ 可用 |
| 基本面 | 财务指标等 | `fundamentals.*` | 东财/同花顺 | ✅ 可用 |

### ⚠️ 已知限制

- 部分接口可能需要代理才能访问（push2.eastmoney.com 被限制时）
- 如有代理，设置环境变量 `http_proxy` 和 `https_proxy`
- 请合理请求频率，避免被封

## 使用示例

### 1. 个股实时行情
```bash
uv run python -m scripts.cli spot --symbol 600000
```

### 2. 历史K线
```bash
uv run python -m scripts.cli hist --symbol 600000 --start 20250101 --end 20250227
```

### 3. 个股基本信息
```bash
uv run python -m scripts.cli info --symbol 600000
```

### 4. 大盘指数
```bash
uv run python -m scripts.cli index --symbol 000001
```

### 5. 财经资讯（不同类型）
```bash
# 个股新闻
uv run python -m scripts.cli news --symbol 600000 --type stock

# 市场新闻
uv run python -m scripts.cli news --type market --limit 100

# 财联社电报
uv run python -m scripts.cli news --type cls --limit 100

# 财经早餐
uv run python -m scripts.cli news --type breakfast --limit 100

# 同花顺直播
uv run python -m scripts.cli news --type ths --limit 100
```

### 6. Python 模块调用示例
```python
from scripts import market_summary, minute, technical

# 市场总貌
sse_data = market_summary.get_sse_summary()
szse_data = market_summary.get_szse_summary()

# 分钟K线
minute_data = minute.get_minute('000001', period=5)

# 分时数据
intraday_data = technical.get_intraday('000001')
```

## News 类型说明

| 类型 | 说明 | 数据源 |
|------|------|--------|
| stock | 个股新闻 | 新浪 |
| market | 全市场新闻 | 东财 |
| cls | 财联社电报 | 财联社 |
| breakfast | 财经早餐 | 东财 |
| global | 全球快讯 | 东财 |
| sina | 全球快讯 | 新浪 |
| futu | 富途快讯 | 富途 |
| ths | 同花顺直播 | 同花顺 |

## 注意事项

1. **数据源限制**：部分接口需要代理才能访问
2. **代理设置**：如有代理，设置环境变量 `http_proxy` 和 `https_proxy`
3. **Rate Limit**：请合理请求频率，避免被封
