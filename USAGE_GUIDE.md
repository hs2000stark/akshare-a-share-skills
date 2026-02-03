# AKShare A股数据查询技能使用指南

## 概述
本技能用于查询A股市场的实时行情、历史K线、个股信息等数据，支持多个数据源（东方财富、新浪、腾讯、雪球）。

## 注意事项
1. **子公司股票代码**：部分公司如平安证券是大型集团的子公司，没有独立的股票代码，需查询母公司股票（如中国平安601318）
2. **网络稳定性**：查询大量数据时可能遇到网络连接问题，可适当降低查询频率
3. **日期格式**：所有日期参数格式为YYYYMMDD（如20250101）

## 常用查询模式

### 1. 个股基本信息查询
```bash
# 方法1：使用CLI（可能有导入问题时使用方法2）
uv run scripts/cli.py info --symbol 601318

# 方法2：直接运行Python模块（推荐用于避免导入错误）
uv run python -c "
from scripts.stock_info import get_stock_info
result = get_stock_info('601318')
print(result)
"
```

### 2. 实时行情查询
```bash
# 方法1：使用CLI
uv run scripts/cli.py spot --symbol 601318

# 方法2：直接运行Python模块
uv run python -c "
from scripts.spot import get_spot
result = get_spot('601318')
print(result)
"
```

### 3. 历史K线数据查询
```bash
# 查询最近N个交易日数据
uv run python -c "
import sys
sys.path.append('.')
from scripts.hist import get_hist
import datetime

# 计算日期范围
end_date = datetime.datetime.now().strftime('%Y%m%d')
start_date = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y%m%d')

result = get_hist('601318', start_date, end_date, 'daily', '', 'em')
recent_data = result['data'][-5:] if len(result['data']) >= 5 else result['data']

for item in recent_data:
    import pandas as pd
    date_str = pd.to_datetime(item['日期'], unit='ms').strftime('%Y-%m-%d')
    print(f'{date_str}: 开盘 {item[\"开盘\"]}, 收盘 {item[\"收盘\"]}, 最高 {item[\"最高\"]}, 最低 {item[\"最低\"]}, 涨跌幅 {item[\"涨跌幅\"]}%')
"
```

## 数据源选择建议

| 数据源 | 优点 | 缺点 | 适用场景 |
|--------|------|------|----------|
| em (东方财富) | 数据最全面，更新及时 | 相对稳定 | 日常查询首选 |
| sina (新浪) | 历史数据丰富 | 可能IP限制 | 备选方案 |
| tx (腾讯) | 数据稳定 | 更新略慢 | 历史数据查询 |
| xq (雪球) | 个股信息详细 | 实时性一般 | 个股深度分析 |

## 实用代码片段

### 快速查询最近5个交易日数据
```python
import sys
sys.path.append('.')
from scripts.hist import get_hist
import datetime

def get_recent_n_days(symbol, n=5):
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=n*2)).strftime('%Y%m%d')
    
    result = get_hist(symbol, start_date, end_date, 'daily', '', 'em')
    recent_data = result['data'][-n:] if len(result['data']) >= n else result['data']
    
    import pandas as pd
    formatted_data = []
    for item in recent_data:
        date_str = pd.to_datetime(item['日期'], unit='ms').strftime('%Y-%m-%d')
        formatted_item = {
            'date': date_str,
            'open': item['开盘'],
            'close': item['收盘'],
            'high': item['最高'],
            'low': item['最低'],
            'change_pct': item['涨跌幅'],
            'volume': item['成交量']
        }
        formatted_data.append(formatted_item)
    
    return formatted_data

# 使用示例
recent_5days = get_recent_n_days('601318', 5)
for day in recent_5days:
    print(f"{day['date']}: {day['open']} -> {day['close']} ({day['change_pct']}%)")
```

### 综合查询模板
```python
import sys
sys.path.append('.')
from scripts.stock_info import get_stock_info
from scripts.spot import get_spot
from scripts.hist import get_hist
import datetime

def comprehensive_query(symbol):
    # 基本信息
    basic_info = get_stock_info(symbol)
    
    # 实时行情
    real_time = get_spot(symbol)
    
    # 历史数据（最近5天）
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y%m%d')
    hist_data = get_hist(symbol, start_date, end_date, 'daily', '', 'em')
    recent_hist = hist_data['data'][-5:] if len(hist_data['data']) >= 5 else hist_data['data']
    
    return {
        'basic_info': basic_info,
        'real_time': real_time,
        'recent_hist': recent_hist
    }

# 使用示例
result = comprehensive_query('601318')
print("基本信息:", result['basic_info']['info'])
print("实时行情:", result['real_time']['quote'])
```

## 故障排除

### 常见错误及解决方案

1. **Import Error**: 尝试直接运行Python模块而非CLI
2. **Connection Reset**: 降低查询频率，稍后再试
3. **No Data Returned**: 检查股票代码是否正确，考虑节假日等因素
4. **CLI Import Issues**: 使用 `uv run python -c` 直接调用模块

## 数据解读

### 重要指标说明
- **总市值** = 当前股价 × 总股本，反映公司整体价值
- **流通市值** = 当前股价 × 流通股数，反映流通股票价值
- **换手率** = (成交量 ÷ 流通股数) × 100%，反映股票流动性
- **量比** = 当日成交量 ÷ 前5日平均成交量，反映放量情况
- **振幅** = (最高价 - 最低价) ÷ 昨收 × 100%，反映当日波动程度

## 使用技巧

1. **批量查询**：使用循环查询多只股票
2. **定时查询**：结合cron任务定期获取数据
3. **数据对比**：同时查询多日数据进行趋势分析
4. **异常处理**：添加try-catch处理网络异常