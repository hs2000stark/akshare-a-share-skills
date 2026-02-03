---
name: akshare-a-share
description: 查询 A 股实时行情、历史 K 线、个股信息与市场总貌（支持多数据源：东方财富/新浪/腾讯/雪球）
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["uv"]}}}
---

# AKShare A 股数据查询

当用户需要查询以下信息时使用本 skill：
- 个股基本信息（市值、行业、上市时间、PE/PB）
- 实时行情（最新价、涨跌幅、五档盘口）
- 历史 K 线（日/周/月，支持复权）
- 分时/分钟数据
- 市场总貌（上交所/深交所概览）

## 前置条件

```bash
cd clawdbot/skills/akshare-a-share
uv sync  # 安装 akshare、pandas 依赖
```

## 数据源说明

| 数据源 | 说明 | 特点 |
|-------|------|------|
| `em` (东方财富) | 默认，数据最全面 | 实时性较好 |
| `sina` (新浪) | 新浪财经 | 可能有 IP 限制 |
| `tx` (腾讯) | 腾讯证券 | 历史数据为主 |
| `xq` (雪球) | 雪球财经 | 个股信息详细 |

## 调用方式

### 1. 个股基本信息

获取指定股票的详细信息。

```bash
# 东方财富源（默认）
uv run scripts/cli.py info --symbol 000001

# 雪球源
uv run scripts/cli.py info --symbol 000001 --source xq
```

### 2. 实时行情

查询股票实时报价或全市场行情列表。

```bash
# 单只股票五档盘口（东方财富）
uv run scripts/cli.py spot --symbol 000001

# 单只股票（指定数据源）
uv run scripts/cli.py spot --symbol 600000 --source sina

# 全市场行情（东方财富）
uv run scripts/cli.py spot --all

# 全市场行情（新浪）
uv run scripts/cli.py spot --all --source sina
```

### 3. 历史 K 线

获取股票历史行情数据（日/周/月 K 线）。

```bash
# 东方财富源（默认）
uv run scripts/cli.py hist --symbol 000001 --start 20230101 --end 20231231 --adjust hfq

# 腾讯源
uv run scripts/cli.py hist --symbol 000001 --start 20230101 --end 20231231 --source tx

# 新浪源
uv run scripts/cli.py hist --symbol 000001 --start 20230101 --end 20231231 --source sina
```

### 4. 分时/分钟数据

获取股票分时或分钟级别数据。

```bash
# 分钟数据（东方财富，1/5/15/30/60分钟）
uv run scripts/cli.py minute --symbol 000001 --period 5

# 分钟数据（新浪）
uv run scripts/cli.py minute --symbol 000001 --period 1 --source sina

# 日内分时
uv run scripts/cli.py intraday --symbol 000001
```

### 5. 市场总貌

查询上交所或深交所的整体市场数据。

```bash
# 上海证券交易所总貌
uv run scripts/cli.py summary --market sse

# 深圳证券交易所总貌
uv run scripts/cli.py summary --market szse --date 20250619
```

## 参数约定

| 参数 | 说明 | 示例 |
|------|------|------|
| symbol | 股票代码，不带市场前缀 | `000001`, `603777` |
| start | 开始日期，YYYYMMDD | `20230101` |
| end | 结束日期，YYYYMMDD | `20231231` |
| adjust | 复权方式：`""` / `qfq` / `hfq` | 见上方说明 |
| period | K线周期：`daily` / `weekly` / `monthly` | `daily` |
| market | 市场标识：`sh` / `sz` / `bj` / `all` | `sz` |
| date | 查询日期，YYYYMMDD | `20250619` |
| source | 数据源：`em` / `sina` / `tx` / `xq` | `em` |
| minute_period | 分钟周期：`1` / `5` / `15` / `30` / `60` | `5` |

## 复权说明

| 复权类型 | 说明 | 适用场景 |
|---------|------|---------|
| `""` (不复权) | 原始价格，存在除权除息缺口 | 简单查看 |
| `qfq` (前复权) | 当前价不变，历史价调整 | 看盘、指标叠加 |
| `hfq` (后复权) | 历史价不变，当前价调整 | **量化研究推荐** |

## 返回格式

所有命令输出 JSON 格式，主要字段说明：

### 个股信息 (`info`)
| 字段 | 说明 |
|------|------|
| 最新 | 最新价 |
| 股票代码 | 证券代码 |
| 股票简称 | 股票名称 |
| 总股本 | 总股本（股） |
| 流通股 | 流通股本（股） |
| 总市值 | 总市值（元） |
| 流通市值 | 流通市值（元） |
| 行业 | 所属行业 |
| 上市时间 | 上市日期（YYYYMMDD） |

### 实时行情 (`spot`)
| 字段 | 说明 |
|------|------|
| 代码 | 股票代码 |
| 名称 | 股票名称 |
| 最新价 | 最新成交价 |
| 涨跌幅 | 涨跌幅（%） |
| 涨跌额 | 涨跌额 |
| 成交量 | 成交量（手） |
| 成交额 | 成交额（元） |
| 市盈率-动态 | PE |
| 市净率 | PB |
| 总市值 | 总市值（元） |
| 流通市值 | 流通市值（元） |

### 历史 K 线 (`hist`)
| 字段 | 说明 |
|------|------|
| 日期 | 交易日期 |
| 股票代码 | 证券代码 |
| 开盘 | 开盘价 |
| 收盘 | 收盘价 |
| 最高 | 最高价 |
| 最低 | 最低价 |
| 成交量 | 成交量（手） |
| 成交额 | 成交额（元） |
| 振幅 | 振幅（%） |
| 涨跌幅 | 涨跌幅（%） |
| 涨跌额 | 涨跌额 |
| 换手率 | 换手率（%） |

### 市场总貌 (`summary`)
| 字段 | 说明 |
|------|------|
| 项目 | 统计项目 |
| 股票/科创板/主板 | 对应数值 |

## 数据来源

- 数据来源：AKShare（东方财富、新浪财经、腾讯证券、雪球等）
- 实时数据会有延迟，非交易所官方实时数据
- 当前交易日数据需在收盘后获取
- 新浪源频繁调用可能被临时封 IP，建议增加时间间隔
