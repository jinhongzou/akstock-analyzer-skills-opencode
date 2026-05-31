# Market Systemic Risk - 市场系统性风险分析

## OVERVIEW
A股市场系统性风险的多维度采集 + 评估框架。分析原始数据由 AI 根据 SKILL.md 自行评估风险等级。

## STRUCTURE
```
market-systemic-risk/
├── main.py                    # 入口：协调各采集器 + 输出报告
├── collect_macro.py           # 宏观经济数据采集（GDP/CPI/PPI/PMI/失业率/货币供应）
├── collect_structure.py       # 市场结构数据采集（全市场PE/PB/市值/融资余额等）
├── collect_capital_flow.py    # 资金流动数据采集（北向资金/两融等）
├── collect_technical.py       # 技术面数据采集（上证PE/全市破净率等）
├── collect_history.py         # 历史案例数据（参考数据，不做判断）
├── guides/                    # SKILL.md 引用的评估指南
│   ├── 01-macro-analysis.md
│   ├── 02-market-structure.md
│   ├── 03-capital-flow.md
│   ├── 04-technical-signals.md
│   ├── 05-historical-cases.md
│   └── 06-action-recommendations.md
```

## WHERE TO LOOK

| 维度 | 文件 | 行数 |
|------|------|------|
| 入口协调 | `main.py` | 103行 |
| 宏观经济 | `collect_macro.py` | 167行 |
| 市场结构 | `collect_structure.py` | 198行 |
| 资金流动 | `collect_capital_flow.py` | 181行 |
| 技术面 | `collect_technical.py` | 190行 |
| 历史案例 | `collect_history.py` | 160行 |

## CONVENTIONS

- 采集器职责：只返回原始数值和简单计算（同比/环比/分位），不做风险判断
- 风险判定全部由 AI 在调用 `skill(name="market-systemic-risk")` 时根据 SKILL.md 指导自行完成
- `collect_*.py` 各文件独立可测，互不依赖
- 使用时通过 `MarketSystemicRiskAnalyzer`（在 `analyzers/market.py` 中）协调各采集器

## ANTI-PATTERNS

- 严禁在采集器代码中添加"高风险""预警"等判断字符串
- 不要修改 guides/ 目录文件（由 SKILL.md 引用，修改需用户确认）
