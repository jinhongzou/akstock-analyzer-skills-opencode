# Industry Analysis - 行业分析

## OVERVIEW
A股行业板块多维度分析：排行、资金流、估值、成分股、轮动。`IndustryAnalyzer`（`analyzers/industry.py`）提供数据获取，此目录的 main.py 协调采集流程。

## STRUCTURE
```
industry-analysis/
├── main.py                         # 入口：协调 4 个采集器 + 格式化输出
├── collect_industry_spot.py        # 行业实时行情（涨幅排行/资金流向）
├── collect_industry_detail.py      # 行业详情（成分股/板块估值）
├── collect_single_industry.py      # 单行业深度分析（成分股基本面聚合）
├── guides/
│   ├── 00-industry-name-list.md
│   ├── 01-industry-ranking.md
│   ├── 02-industry-fundflow.md
│   ├── 03-industry-valuation.md
│   ├── 04-industry-rotation.md
│   └── 05-single-industry-deep-dive.md
```

## WHERE TO LOOK

| 模块 | 文件 | 行数 | 说明 |
|------|------|------|------|
| 入口+输出 | `main.py` | 370行 | 协调流程+格式化 |
| 行业实时行情 | `collect_industry_spot.py` | 195行 | 涨幅排行+资金流 |
| 行业详情 | `collect_industry_detail.py` | 127行 | 成分股+板块估值 |
| 单行业深度 | `collect_single_industry.py` | 421行 ⚠️ | 成分股基本面聚合 |
| 数据类 | `IndustryAnalyzer` (analyzers/industry.py) | 591行 | 数据获取底层 |

## CONVENTIONS

- `collect_*.py` 只负责数据采集和简单计算，不包含分析判断
- 分析框架（评分卡、阈值、等级）定义在 `SKILL.md` 中
- `guides/` 内容供 SKILL.md 引用，修改需用户确认
- `IndustryAnalyzer` 是底层数据类，`main.py` 调用它进行数据采集

## NOTES

- `collect_single_industry.py`(421行) 和 `IndustryAnalyzer`(591行) 是热点文件
- 行业分类基于东方财富行业板块
- 资金流数据来自东方财富接口，可能有延迟
