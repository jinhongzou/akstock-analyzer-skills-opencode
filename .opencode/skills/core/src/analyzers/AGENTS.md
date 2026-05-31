# Analyzers - A股分析器层

## OVERVIEW
9 个 Analyzer 类，每个对应一个分析维度。数据获取 + 计算逻辑封装在类内部，返回结构化 dict/DataFrame。

## STRUCTURE
```
analyzers/
├── __init__.py         # 导出所有 Analyzer 类
├── stock.py            # StockAnalyzer - 个股行情/估值/行业归属/52周分布/PE锚点
├── market.py           # MarketAnalyzer / MarketSystemicRiskAnalyzer - 市场整体/系统性风险
├── technical.py        # TechnicalAnalyzer - MA50/MA200 金叉死叉 + RSI14
├── financial.py        # FinancialAnalyzer - 财务健康6维评分 + ROCE计算
├── dividend.py         # DividendAnalyzer - 分红配送详情
├── shareholder.py      # ShareholderAnalyzer - 十大股东/增减持/质押/回购
├── industry.py         # IndustryAnalyzer - 行业排行/资金流/估值/轮动
├── news.py             # NewsRiskAnalyzer - 新闻风险分析
├── etf.py              # NationalTeamFundTracker - 国家队ETF持仓追踪
```

## WHERE TO LOOK

| 分析维度 | 类 | 文件 |
|---------|-----|------|
| 个股估值 | `StockAnalyzer` | `stock.py` (295行) |
| 技术分析 | `TechnicalAnalyzer` | `technical.py` (89行) |
| 财务健康 | `FinancialAnalyzer` | `financial.py` (184行) |
| 分红配送 | `DividendAnalyzer` | `dividend.py` (317行) |
| 市场整体 | `MarketAnalyzer` | `market.py` (473行) |
| 系统性风险 | `MarketSystemicRiskAnalyzer` | `market.py` (473行) |
| 行业分析 | `IndustryAnalyzer` | `industry.py` (591行) ⚠️ 最大文件 |
| 新闻风险 | `NewsRiskAnalyzer` | `news.py` (90行) |
| 股东分析 | `ShareholderAnalyzer` | `shareholder.py` (283行) |
| 国家队ETF | `NationalTeamFundTracker` | `etf.py` (310行) |

## CONVENTIONS

- 所有类通过 `analyzers/__init__.py` 统一导出（`__all__` 列表）
- 数据源：Tushare Pro 优先，akshare 替补（见 AGENTS.md 根文档数据源策略）
- 返回值：结构化 dict/DataFrame，**不含分析判断**（判断全在 SKILL.md）
- 文件名即类名小写 + `_analyzer` 后缀（例外：`etf.py` → `NationalTeamFundTracker`）
- 大文件（>300行）：`industry.py`(591), `market.py`(473), `dividend.py`(317), `etf.py`(310), `stock.py`(295)

## NOTES

- 东方财富接口不稳定，Tushare 优先
- 勿在此层添加"预警""危险""建议"等判断逻辑
