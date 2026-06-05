<div align="right">
  <b><a href="#chinese">🇨🇳 中文</a></b> | <a href="#english">🇺🇸 English</a>
</div>

<a id="chinese"></a>

# 基于Opencode的 A股分析 Skill 集

基于 **tushare/akshare** 免费数据源的 A 股多维度分析 OpenCode Skills，覆盖 **盈利能力 (ROCE) / 财务安全 / 估值合理性 / 技术面 / 股东分析 / 分红 / 新闻风险 / A股系统性风险等** 维度。**回测** SKILL 开发中...

> 内置 **akshare-docs** Skill，可根据用户的分析需求自由查询 akshare 的 2000+ 个免费接口，找到所需数据源，无需翻阅文档


## 项目优势

| # | 优势 | 说明 |
|---|------|------|
| 1 | 🆓 **零成本，全免费** | 所有数据基于开源 tushare/akshare 接口，其中akshare无需任何付费 API Token 即可获取 A 股行情、财务、估值等全维度数据 |
| 2 | 🔍 **akshare-docs 按需查询** | 内置 `akshare-docs` Skill，可根据你的分析需求自由查询 akshare 的 2000+ 个免费接口，找到所需数据源，无需翻阅文档 |
| 3 | 🧩 **24+ 独立 Skill，自由组合** | 覆盖行情/财务/技术/股东/分红/风控/期货等维度，既可单独调用，也可通过 `report-builder` 一键输出完整报告 |
| 4 | 🔄 **双数据源兜底** | Tushare Pro 优先 + akshare 自动降级，单个接口异常不影响分析流程 |
| 5 | 📊 **交互式图表** | 支持 ECharts HTML 图表生成（国家队ETF追踪、碳酸锂期货价格走势等），可视化更直观 |
| 6 | 🐍 **纯 Python 实现** | 仅需 `pip install`，无需额外服务或环境配置，命令行即可运行 |

## 特点

- 🀆 **23 个独立 Skill**：可按需单独使用，也可一键输出完整投资报告
- 🔆 **共享核心架构**：所有 Skill 统一引用 `core/` 核心逻辑层，保证数据一致性与零代码重复
- 🆓 **6 维评分体系**：盈利能力 / 财务安全 / 估值合理性 / 技术面 / 业务前景 / 新闻风险，满分 120 分
- 🆗 **多数据源融合**：Tushare Pro（个股估值/行情🔄）、新浪财经（财务报表/K线）、东方财富（新闻/分红）、乐咕（市场PE）
- 🆕 **纯 Python 实现**：无需额外服务，命令行即可运行
- 🆟 **邮件发送**：支持分析报告自动发送到指定邮箱

---

## 包含 Skill

| Skill | 功能 | 输入 | 核心模块 |
|-------|------|------|----------|
| `stock-analyzer` | 个股估值（PE/PB/股息率/行业分析） | 股票代码 | `StockAnalyzer` |
| `technical-analyzer` | 技术指标（MA50/MA200 金叉死叉 + RSI14） | 股票代码 | `TechnicalAnalyzer` |
| `risk-analysis` | 综合风控（新闻风险+价格分位数分析） | 股票代码 | `NewsRiskAnalyzer` + 分位数计算 |
| `roce-calculator` | 近 10 年 ROCE（资本回报率）趋势 | 股票代码 | `FinancialAnalyzer` |
| `a-dividend-analyzer` | A股分红配送（送转/现金分红/股息率/关键日期） | A股代码 | `DividendAnalyzer` |
| `market-analyzer` | A 股市场整体状况（平均PE/上证指数MA20/MA50） | 无 | `MarketAnalyzer` |
| `market-systemic-risk` | 市场系统性风险分析（多维度综合预警） | 无 | `MarketSystemicRiskAnalyzer` |
| `industry-analysis` | 行业分析（排行/资金流/估值/成分股/轮动） | 无 | `IndustryAnalyzer` |
| `shareholder-deep` | 股东深度分析 | 股票代码 | `ShareholderAnalyzer` |
| `valuation-anchor` | 估值锚点分析 | 股票代码 | `StockAnalyzer` |
| `email-sender` | 发送邮件（支持附件） | 收件人/主题/内容 | SMTP |
| `pdf-converter` | PDF 转 Markdown 格式 | PDF 路径 | PDF 解析 |
| `akshare-docs` | AKshare API 文档查询 | 关键词 | 文档检索 |
| `web-search` | 网络实时搜索 | 查询内容 | Tavily |
| `cninfo-search` | 巨潮资讯网公告搜索（含PDF下载链接） | 股票代码或公司名称 | cninfo API |
| `chronos-timeline` | CHRONOS 事件时间线分析（不含股价数据，支持 AI 辅助语义匹配） | 股票代码 + 关键词 | cninfo + 新闻 |
| `buffett-checklist` | 巴菲特7关检查清单（聚合9个分析器数据） | 股票代码 | 多Analyzer聚合 |
| `financial-analysis` | 深度财务分析（6维度评分卡+4项红旗筛查） | 股票代码 | `FinancialAnalyzer` |
| `percentile-analyzer` | 历史分位数分析（3月/1年/3年/5年） | 股票代码 | 分位数计算 |
| `report-builder` | 综合分析+报告生成（协调8个分析Skill） | 股票代码 | 多Analyzer聚合 |
| `tushare-data` | Tushare数据研究（口语化查询→数据获取） | 自然语言查询 | Tushare Pro |
| `national-team-fund-tracker` | 国家队ETF持仓规模月度追踪 | 无 | `NationalTeamFundTracker` |
| `darwinian_value_investing` | 达尔文价值投资（进化论选股框架） | 股票代码 | 多Analyzer聚合 |
| `munger_value_investing` | 芒格价值投资框架 | 股票代码 | 多Analyzer聚合 |

---

## 目录结构

```
stock-analyzer-skills_tushare/           # 项目根目录
├── .opencode/
│   └── skills/
│       ├── core/                        # 向后兼容导出层（委托给 src/）
│       │   └── __init__.py              #   26 个包装函数 + 类导出
│       │   └── src/                     # 核心源代码目录
│       │       ├── __init__.py
│       │       ├── config/
│   │       │   └── .env             # ⚠️ 统一配置文件（Tushare Token/SMTP/Tavily API Key）
│       │       ├── analyzers/           # 分析器层，9 个 Analyzer 类
│       │       │   ├── __init__.py
│       │       │   ├── industry.py      # IndustryAnalyzer（行业分析）
│       │       │   ├── market.py        # MarketAnalyzer（市场分析）
│       │       │   ├── technical.py     # TechnicalAnalyzer（技术分析）
│       │       │   ├── news.py          # NewsRiskAnalyzer（新闻风险）
│       │       │   ├── dividend.py      # DividendAnalyzer（分红配送）
│       │       │   ├── financial.py     # FinancialAnalyzer（财务健康 + ROCE）
│       │       │   ├── stock.py         # StockAnalyzer（个股估值 + 估值锚点）
│       │       │   ├── shareholder.py   # ShareholderAnalyzer（股东分析）
│       │       │   └── etf.py           # NationalTeamFundTracker（国家队ETF）
│       │       ├── infra/               # 基础设施层
│       │       │   ├── __init__.py
│       │       │   ├── cache.py         # CacheManager（缓存）
│       │       │   └── report.py        # ReportGenerator（评分 + 报告导出）
│   │       └── skills/              # 19 个 Skill 入口（薄封装层）
│   │           ├── stock-analyzer/main.py
│       │           ├── technical-analyzer/main.py
│       │           ├── a-dividend-analyzer/main.py
│       │           ├── buffett-checklist/main.py
│       │           ├── roce-calculator/main.py
│       │           ├── market-analyzer/main.py
│       │           ├── percentile-analyzer/main.py
│       │           ├── risk-analysis/main.py
│       │           ├── shareholder-deep/main.py
│       │           ├── valuation-anchor/main.py
│       │           ├── email-sender/main.py
│       │           ├── pdf-converter/main.py
│       │           ├── akshare-docs/main.py
│       │           ├── market-systemic-risk/main.py
│       │           ├── industry-analysis/main.py
│       │           ├── national-team-fund-tracker/main.py
│       │           ├── web-search/main.py
│       │           ├── cninfo-search/main.py
│       │           └── chronos-timeline/main.py
│       └── [skill-name]/             # 各 Skill 目录（SKILL.md + 旧入口）
│           ├── SKILL.md
│           └── scripts/              # 已迁移到 core/src/skills/
├── output/                            # 生成的分析报告（与 .opencode 同级）
├── AGENTS.md
└── README.md
```

---

### 架构原则

| 层级 | 目录 | 职责 |
|------|------|------|
| **向后兼容层** | `core/__init__.py` | 27 个包装函数 + 11 个类导出，委托给下层 Analyzer 类 |
| **分析器层** | `core/src/analyzers/` | 9 个 Analyzer 类，数据获取 + 计算逻辑 |
| **基础设施层** | `core/src/infra/` | CacheManager + ReportGenerator |
| **入口层** | `core/src/skills/` | 19 个 skill 的 `main.py`，参数解析 + 格式化输出 |

---

## 安装方式

### 前置依赖

```bash
pip install akshare pandas
```

### 方式 1：全局安装（本机所有 OpenCode 项目可用）

**Windows**：
```cmd
mklink /D "%USERPROFILE%\.config\opencode\skills\stock-analyzer" "C:\Users\Lenovo\Desktop\stock-analyzer-skills"
```

**Linux/macOS**：
```bash
ln -s /path/to/stock-analyzer-skills ~/.config/opencode/skills/stock-analyzer
```

### 方式 2：项目级安装（仅当前项目可用）

将整个 `.opencode/` 目录复制到目标项目根目录：

```bash
cp -r stock-analyzer-skills/.opencode /path/to/target-project/
```

### 方式 3：Git 子模块（推荐团队使用）

```bash
git submodule add <仓库URL> .opencode/skills/stock-analyzer
```

---

## 配置文件

所有API密钥和SMTP配置统一在以下文件中管理：

```
.opencode/skills/core/src/config/.env
```

包含以下配置项：

| 配置项 | 说明 |
|--------|------|
| `TUSHARE_TOKEN` | Tushare Pro 数据接口令牌（财务/行情/估值） |
| `SMTP_HOST` / `SMTP_PORT` | 邮件服务器地址和端口 |
| `SMTP_USER` / `SMTP_PASSWORD` | 邮件发送账号和密码 |
| `TAVILY_API_KEY` | Web Search 搜索接口密钥 |
| `OUTPUT_DIR` | 分析报告输出目录（默认：`output/`） |

> **注意**：所有 Skill 共用此配置文件，修改后无需重启即可生效。

---

## 使用方式

### OpenCode 调用

在 OpenCode 对话框中直接调用 Skill：

```
skill(name="stock-analyzer")
skill(name="technical-analyzer")
skill(name="buffett-checklist")
skill(name="financial-analysis")
skill(name="roce-calculator")
skill(name="a-dividend-analyzer")
skill(name="percentile-analyzer")
skill(name="risk-analysis")
skill(name="shareholder-deep")
skill(name="valuation-anchor")
skill(name="market-analyzer")
skill(name="market-systemic-risk")
skill(name="industry-analysis")
skill(name="report-builder")
skill(name="email-sender")
skill(name="pdf-converter")
skill(name="akshare-docs")
skill(name="tushare-data")
skill(name="web-search")
skill(name="national-team-fund-tracker")
skill(name="darwinian_value_investing")
skill(name="munger_value_investing")
skill(name="cninfo-search")
skill(name="chronos-timeline")
```

### 命令行运行

```bash
# 单独使用各 Skill
python .opencode/skills/core/src/skills/stock-analyzer/main.py 600519
python .opencode/skills/core/src/skills/technical-analyzer/main.py 600519
python .opencode/skills/core/src/skills/buffett-checklist/main.py 600519
python .opencode/skills/core/src/skills/roce-calculator/main.py 600519
python .opencode/skills/core/src/skills/a-dividend-analyzer/main.py 600519
python .opencode/skills/core/src/skills/percentile-analyzer/main.py 600519
python .opencode/skills/core/src/skills/risk-analysis/main.py 600519
python .opencode/skills/core/src/skills/shareholder-deep/main.py 000651
python .opencode/skills/core/src/skills/valuation-anchor/main.py 600519
python .opencode/skills/core/src/skills/market-analyzer/main.py
python .opencode/skills/core/src/skills/market-systemic-risk/main.py
python .opencode/skills/core/src/skills/industry-analysis/main.py
python .opencode/skills/core/src/skills/email-sender/main.py "收件人" "主题" "内容"
python .opencode/skills/core/src/skills/pdf-converter/main.py "file.pdf"
python .opencode/skills/core/src/skills/akshare-docs/main.py "stock_zh_a_spot"
python .opencode/skills/core/src/skills/web-search/main.py "查询内容"
python .opencode/skills/core/src/skills/national-team-fund-tracker/main.py
python .opencode/skills/core/src/skills/cninfo-search/main.py 600519
python .opencode/skills/core/src/skills/chronos-timeline/main.py 600519 回购
python .opencode/skills/core/src/skills/chronos-timeline/main.py 600338 锂矿 --relax --export-candidates cand.json
python .opencode/skills/core/src/skills/chronos-timeline/main.py --build-report annotated.json
```

---

## 输出示例

### 综合评分体系

| 维度 | 满分 | 评估内容 | 评分逻辑 |
|------|------|---------|---------|
| 盈利能力 | 20 | ROCE 绝对值 + 趋势 | ROCE >20% 得 20 分；趋势恶化（近 3 年降 >50%）扣 5 分 |
| 财务安全 | 20 | 流动比率 + 资产负债率 | 流动比率 >2 加 6 分；<0.5 扣 6 分；负债率 <30% 加 4 分 |
| 估值合理性 | 20 | PE 水平 | PE <15 得 20 分；15-25 得 15 分；25-40 得 10 分；>40 得 5 分 |
| 技术面 | 20 | MA 均线信号 + RSI | 金叉 +5 分；死叉 -3 分；超卖 +3 分；超买 -3 分 |
| 业务前景 | 20 | 行业地位 + 增长潜力 | 行业龙头 +10 分；高增长 +10 分 |
| 新闻风险 | 20 | 负面新闻数量 | 有诚信风险得 5 分；有经营风险得 12 分；无风险得 20 分 |

| 总分 | 评级 | 建议 |
|------|------|------|
| 80-100 | A 优秀 | 积极关注，可考虑买入 |
| 65-79 | B 良好 | 基本面良好，逢低布局 |
| 50-64 | C 一般 | 观望为主，等待更好时机 |
| 35-49 | D 较差 | 风险较高，谨慎对待 |
| 0-34 | E 危险 | 回避，风险过大 |

**评分特点**：
- ROCE 趋势恶化自动扣分（近 3 年下降 >50%）
- 流动比率权重加倍（短期偿债能力是关键风险）
- 业务前景作为新增维度评估行业竞争⼒

---

## 各 Skill 详细说明

### roce-calculator

计算股票近 10 年 ROCE（Return on Capital Employed，资本回报率）。

**核心公弌**：
```
ROCE = EBIT / 投入资本
投入资本 = 总资产 - 流动负债
EBIT = 净利润 + 利息费用 + 所得税
```

**ROCE 参考标准**：

| 范围 | 评价 |
|------|------|
| > 20% | 优秀 |
| 15% - 20% | 良好 |
| 10% - 15% | 一般 |
| < 10% | 较差 |

### market-analyzer

分析 A 股市场整体状况，无需输入股票代码。

**输出内容**：
- 全市场平均市盈率（乐咕数据）
- 上证指数 MA20 / MA50
- 牛熊判断：MA20 > MA50 → 牛市 | MA20 < MA50 → 熊市

### stock-analyzer

获取个股实时行情和估值数据。

**输出指标**：
- 股票名称 / 所属行业 / 现价 / 涨跌幅
- PE(动/静/TTM) / PB / 股息率(TTM)
- 总市值 / 每股收益 / 每股净资产
- 基于 PE 和涨跌幅的买卖建议

### technical-analyzer

分析股票技术指标。

**输出指标**：
- **MA 均线系统**：MA50 / MA200 金叉（Bullish）或死叉（Bearish）
- **RSI(14)**：>70 超买 | <30 超卖 | 30-70 中性

### risk-analysis

综合风控分析，整合新闻风险评估 + 历史分位数分析。

**风险等级**：

| 等级 | 说明 |
|------|------|
| 🔶 高风险 | 财务造假、监管处罚、诚信问题、立案调查等 |
| 🟡 中风险 | 业绩下滑、股东减持、行业政策变化、高管辞职等 |
| 🟢 低风险 | 日常经营、正面新闻等 |

**输出内容**：
- 新闻风险：高/中/低风险统计，诚信风险关键词检测
- 价格分位：近3月/1年/3年/5年价格分位，多周期信号对比
- 综合评分：新闻风险 50% + 价格分位 50%，A-E 评级

**诚信风险关键词**（50+ 个）：财务造假、虚增利润、虚假记载、信披违规、证监会调查、行政处罚、内幕交易、操纵股价、退市风险警示等。

### a-dividend-analyzer

获取A股历年分红配送详情，分析分红连续性和送转/现金分红情况。

**输出内容**：
- 历年分红表格（报告期/预案公告日/股权登记日/除权除息日/方案进度/送转/现金分红/股息率/每股指标/净利润同比）
- 详细每股指标（每股公积金/每股未分配利润/总股本/送股比例/转股比例）
- 分红连续性分析（现金分红年份/送股年份/转股年份/平均股息率/连续性评价）

**送转类型**：
- 送股：用未分配利润转增股本，需缴税
- 转股：用资本公积金转增股本，不缴税
- 现金分红：直接向股东派发现金

### pdf-converter

将 PDF 文件转换为 Markdown 格式，便于阅读和分析。

**功能**：
- PDF 转 Markdown
- 保留表格和格式
- 图表描述提取

### shareholder-deep

股东深度分析，展示十大股东变化趋势、机构持仓、增减持动向、国家队持仓等。

**输出内容**：
- 十大流通股东及其持股比例（近 5 期）
- 国家队持股（中国证券金融、中央汇金）
- 机构/基金持股变化
- 股东增减持变动
- 抛售风险预警

### email-sender

通过 SMTP 协议发送邮件，支持附件。

**使用方式**：
```bash
python .opencode/skills/core/src/skills/email-sender/main.py "收件人" "主题" "内容"
```

**配置**（在 `core/src/config/.env` 统一配置文件中）：
```
SMTP_HOST=smtp.126.com
SMTP_PORT=465
SMTP_USER=your_email@126.com
SMTP_PASSWORD=your_password
```

### buffett-checklist

巴菲特7关检查清单。聚合9个分析器数据，输出原始聚合数据供你独立评估7关。

**7关框架**：
1. **能力圈** — 是否理解这门生意（8分制）
2. **护城河** — 竞争优势持久性（15★制）
3. **管理层** — 管理层可信度（红灯累计）
4. **财务健康** — 5项财务指标（通过数）
5. **安全边际** — 价格是否足够便宜（5项判定）
6. **红旗检查** — 7条红线逐条检测
7. **市场风险** — 当前市场系统性风险（20分制）

**使用方式**：
```bash
python .opencode/skills/core/src/skills/buffett-checklist/main.py 600519
```

### financial-analysis

基于Tushare接口的A股深度财务分析。6维度评分卡 + 4项红旗筛查，可执行的财务健康决策框架。

**评估维度**：盈利能力、偿债能力、运营效率、成长性、现金流质量、分红回报

**红旗筛查**：ROE<10%、资产负债率>70%、经营现金流/净利润<0.5、商誉/净资产>30%

> 仅支持 OpenCode `skill(name="financial-analysis")` 调用

### percentile-analyzer

股票历史分位数分析。计算当前价格在近3月/1年/3年/5年历史分布中的位置，支持多周期对比。

**输出指标**：
- 各周期当前价、最低价、最高价、中位价
- 当前位置分位百分比
- 多周期操作信号一致性分析

**使用方式**：
```bash
python .opencode/skills/core/src/skills/percentile-analyzer/main.py 600519
```

### report-builder

综合分析+报告生成。基于 unified-template 模板协调8个分析Skills，组装生成10章标准投资分析报告（Markdown格式）。

**报告章节**：市场环境→公司概况→行业分析→财务分析→股东分红→估值分析→技术分析→风险提示→综合评分→投资建议

> 支持 `skill(name="report-builder")` 调用，也可通过 email-sender 发送生成的报告附件

### tushare-data

Tushare数据研究工具。面向中文自然语言，将口语化查询转为数据获取、清洗、对比、筛选与导出。

**覆盖场景**：A股行情、财务、估值、资金流、板块概念等

> 仅支持 OpenCode `skill(name="tushare-data")` 调用

### national-team-fund-tracker

国家队ETF持仓规模月度追踪。追踪汇金系重仓的8只核心宽基ETF的份额变化，反映国家队入场/退出的整体规模方向。

**输出内容**：
- 月度总量趋势（总份额变化曲线）
- 单ETF份额变化明细
- 月度环比变化（增减方向）
- 持仓结构分析

**使用方式**：
```bash
python .opencode/skills/core/src/skills/national-team-fund-tracker/main.py
```

### darwinian_value_investing

基于《我从达尔文那里学到的投资知识》的选股与择时框架。将进化论核心概念转化为可执行的商业生态分析与投资决策流程。

> 仅支持 OpenCode `skill(name="darwinian_value_investing")` 调用

### munger_value_investing

芒格价值投资框架。基于多维度数据分析的选股评估体系。

> 仅支持 OpenCode `skill(name="munger_value_investing")` 调用

---

## 已生成报告示例

| 股票代码 | 股票名称 | 评分 | 评级 | 报告文件 |
|----------|----------|------|------|----------|
| 000651 | 格力电器 | — | — | `output/格力电器_000651_综合分析报告.md` |
| 000651 | 格力电器 | 5/6关通过+🟡市场中性 | 推荐买入 | 巴菲特清单检查（本对话） |
| 000333 | 美的集团 | 4/6关通过+🟡市场中性 | 推荐买入 | 巴菲特清单检查（本对话） |

> 报告文件保存在项目根目录 `output/` 下（与 `.opencode/` 同级），可通过邮件发送

---

## 数据源

| 数据源 | API / 函数 | 用途 |
|--------|-----------|------|
| **Tushare Pro** | `pro.daily_basic()` / `pro.daily()` / `pro.stock_basic()` / `pro.fina_indicator()` | 个股估值（PE/PB/股息率/EPS/总市值/行业）⬆主力 |
| **新浪财经** | `akshare.stock_financial_report_sina()` | 三大财务报表 |
| **新浪财经** | `akshare.stock_zh_a_daily()` | 历史 K 线数据 |
| **东方财富** | `akshare.stock_news_em()` | 个股新闻 |
| **东方财富** | `akshare.stock_fhps_detail_em()` | A股分红送配数据 |
| **乐咕** | `akshare.stock_market_pe_lg()` | 市场整体 PE |
| **新浪** | `akshare.stock_zh_index_daily()` | 上证指数日线 |

---

## 注意事项

### 行为守则（所有 Skill 通用）
1. **不确定性必须提问**：遇到模糊需求、缺少参数、多种可能选项时，必须向用户提问澄清，不得替用户做决定
2. **不擅自假设**：不要假设用户意图，必须用问题确认
3. **不擅自执行**：输出报告前先展示关键发现，让用户决定下一步
4. **修改项目级代码须用户确认**：对 `core/src/analyzers/`、`core/src/skills/`、`core/__init__.py` 等核心文件的改动，必须先向用户展示改动计划和预期影响，获得明确许可后方可执行

---

1. **Tushare Pro 已替换雪球估值**：`StockAnalyzer.get_stock_profile()` 使用 Tushare Pro 获取 PE/PB/股息率，不再依赖雪球接口
2. **东方财富接口不稳定**：`stock_zh_a_spot_em()` 和 `stock_zh_a_hist()` 经常超时，优先使用新浪和 Tushare 数据源
3. **财务报表列名**：新浪数据源返回中文列名，内部使用 `safe_get_col()` 模糊匹配
4. **ROCE 计算慢**：需要逐年获取财务报表（每年 2 张表），10 年数据需要 20+ 次网络请求
5. **新闻过滤**：泛市场新闻（"板块"、"概念股"、"主力资金"）不参与个股风险评估
6. **网络请求**：所有数据来自在线接口，需要网络连接；部分接口有频率限制，建议调用间隔 >3 秒

---

## 常见问题

**Q: 运行时报错 "ModuleNotFoundError: No module named 'core'"？**  
A: 确保从项目根目录运行。`core/src/skills/[name]/main.py` 通过 `sys.path.insert(0, ...)` 自动添加 4 层上级目录（到 `.opencode/skills/`）来导入 `core`。始终在项目根目录执行命令即可。

**Q: 财务分析报错 "Expecting value: line 1 column 1"？**  
A: 新浪财经接口偶尔返回非 JSON 响应，属于数据源问题，稍后重试即可。

**Q: ROCE 计算很慢？**  
A: ROCE 需要逐年获取财务报表（每年 2 张表），10 年数据需要 20 次网络请求，请耐心等待。

**Q: 如何添加新的分析维度？**  
A: 在 `core/src/analyzers/` 下新建 Analyzer 类，在 `core/__init__.py` 中添加包装函数，然后在对应 skill 的 `main.py` 中调用即可。

---

## 许可证

MIT

---

<a id="english"></a>

<div align="right">
  <a href="#chinese">🇨🇳 中文</a> | <b><a href="#english">🇺🇸 English</a></b>
</div>

# A-Share Stock Analysis Skill Set for OpenCode

A multi-dimensional A-share stock analysis OpenCode Skill set based on **Tushare Pro** and **akshare** data sources. Covers **profitability (ROCE) / financial safety / valuation / technical analysis / shareholder analysis / dividends / news risk / systemic market risk** dimensions.

> ⚠️ Built-in `akshare-docs` Skill lets you search 2000+ free akshare APIs based on your analysis needs — no documentation hunting.

## Advantages

| # | Advantage | Description |
|---|-----------|-------------|
| 1 | 🆓 **Zero Cost** | All data from free open-source APIs (akshare). No paid tokens required for full-dimensional A-share data access |
| 2 | 🔍 **akshare-docs On-Demand Query** | Built-in `akshare-docs` Skill lets you search 2000+ free akshare APIs based on your analysis needs — no documentation hunting |
| 3 | 🧩 **24+ Independent Skills** | Modular design covering quotes/financials/technicals/shareholders/dividends/risk/futures. Use individually or combine into full reports via `report-builder` |
| 4 | 🔄 **Dual Data Source Fallback** | Tushare Pro preferred + akshare auto-fallback. Single API failure doesn't break analysis |
| 5 | 📊 **Interactive Charts** | ECharts HTML report generation (national team ETF tracker, lithium futures price charts, etc.) for better visualization |
| 6 | 🐍 **Pure Python** | Just `pip install`, no external services or environment setup, runs from command line |

## Features

- 🀆 **24 Independent Skills**: Use individually or combine for a full investment report
- 🔆 **Shared Core Architecture**: All skills share the `core/` logic layer for data consistency and zero code duplication
- 🆓 **6-Dimension Scoring System**: Profitability / Financial Safety / Valuation / Technicals / Business Outlook / News Risk — 120 points total
- 🆗 **Multi-Source Data**: Tushare Pro (valuation/quotas) + Sina Finance (financial statements/K-line) + East Money (news/dividends) + Legu (market PE)
- 🆕 **Pure Python**: No external services needed, runs from command line
- 🆟 **Email Sending**: Send analysis reports to specified email addresses

---

## Included Skills

| Skill | Function | Input | Core Module |
|-------|----------|-------|-------------|
| `stock-analyzer` | Stock valuation (PE/PB/Dividend Yield) | Stock code | `StockAnalyzer` |
| `technical-analyzer` | Technical analysis (MA50/200 crossover + RSI14) | Stock code | `TechnicalAnalyzer` |
| `risk-analysis` | Risk control (news risk + price percentile) | Stock code | `NewsRiskAnalyzer` + percentile calc |
| `roce-calculator` | 10-year ROCE trend | Stock code | `FinancialAnalyzer` |
| `a-dividend-analyzer` | Dividend & stock split history | A-share code | `DividendAnalyzer` |
| `market-analyzer` | Overall market conditions (avg PE, MA20/MA50) | None | `MarketAnalyzer` |
| `market-systemic-risk` | Systemic risk analysis (multi-dimension) | None | `MarketSystemicRiskAnalyzer` |
| `industry-analysis` | Industry ranking/fund flow/valuation/rotation | None | `IndustryAnalyzer` |
| `shareholder-deep` | Deep shareholder analysis | Stock code | `ShareholderAnalyzer` |
| `valuation-anchor` | Valuation anchor analysis | Stock code | `StockAnalyzer` |
| `email-sender` | Send emails (attachment support) | Recipient/Subject/Body | SMTP |
| `pdf-converter` | PDF to Markdown conversion | PDF path | PDF parser |
| `akshare-docs` | AKshare API documentation lookup | Keywords | Doc search |
| `web-search` | Real-time web search | Query text | Tavily |
| `cninfo-search` | CNINFO announcement search (with PDF download links) | Stock code or name | cninfo API |
| `buffett-checklist` | Buffett 7-gate checklist (aggregates 9 analyzers) | Stock code | Multi-analyzer |
| `financial-analysis` | Deep financial analysis (6D scorecard + 4 red flags) | Stock code | `FinancialAnalyzer` |
| `percentile-analyzer` | Historical percentile analysis (3M/1Y/3Y/5Y) | Stock code | Percentile calc |
| `report-builder` | Full report generation (coordinates 8 skills) | Stock code | Multi-analyzer |
| `tushare-data` | Tushare data query (NL query → data) | Natural language | Tushare Pro |
| `national-team-fund-tracker` | National team ETF monthly position tracking | None | `NationalTeamFundTracker` |
| `darwinian_value_investing` | Darwinian value investing (evolutionary stock picking) | Stock code | Multi-analyzer |
| `munger_value_investing` | Munger value investing framework | Stock code | Multi-analyzer |

---

## Directory Structure

```
stock-analyzer-skills_tushare/           # Project root
├── .opencode/
│   └── skills/
│       ├── core/                        # Backward-compat export layer
│       │   └── __init__.py              #   26 wrapper functions + 9 class exports
│       │   └── src/                     # Core source code
│       │       ├── __init__.py
│       │       ├── config/
│   │       │   └── .env             # ⚠️ Config file (Tushare Token/SMTP/Tavily API Key)
│       │       ├── analyzers/           # Analyzer layer, 9 Analyzer classes
│       │       │   ├── __init__.py
│       │       │   ├── industry.py      # IndustryAnalyzer
│       │       │   ├── market.py        # MarketAnalyzer
│       │       │   ├── technical.py     # TechnicalAnalyzer
│       │       │   ├── news.py          # NewsRiskAnalyzer
│       │       │   ├── dividend.py      # DividendAnalyzer
│       │       │   ├── financial.py     # FinancialAnalyzer (financial health + ROCE)
│       │       │   ├── stock.py         # StockAnalyzer (valuation + valuation anchor)
│       │       │   ├── shareholder.py   # ShareholderAnalyzer
│       │       │   └── etf.py           # NationalTeamFundTracker
│       │       ├── infra/               # Infrastructure layer
│       │       │   ├── __init__.py
│       │       │   ├── cache.py         # CacheManager
│       │       │   └── report.py        # ReportGenerator (scoring + exports)
│   │       └── skills/              # 19 skill entry points (thin wrapper)
│   │           ├── stock-analyzer/main.py
│       │           ├── technical-analyzer/main.py
│       │           ├── a-dividend-analyzer/main.py
│       │           ├── buffett-checklist/main.py
│       │           ├── roce-calculator/main.py
│       │           ├── market-analyzer/main.py
│       │           ├── percentile-analyzer/main.py
│       │           ├── risk-analysis/main.py
│       │           ├── shareholder-deep/main.py
│       │           ├── valuation-anchor/main.py
│       │           ├── email-sender/main.py
│       │           ├── pdf-converter/main.py
│       │           ├── akshare-docs/main.py
│       │           ├── market-systemic-risk/main.py
│       │           ├── industry-analysis/main.py
│       │           ├── national-team-fund-tracker/main.py
│       │           ├── web-search/main.py
│       │           └── cninfo-search/main.py
│       └── [skill-name]/             # SKILL.md + legacy scripts
│           ├── SKILL.md
│           └── scripts/
├── output/                            # Generated reports
├── AGENTS.md
└── README.md
```

---

### Architecture

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| **Backward Compat** | `core/__init__.py` | 27 wrapper functions + 11 class exports, delegates to Analyzer classes |
| **Analyzers** | `core/src/analyzers/` | 9 Analyzer classes, data fetching + business logic |
| **Infrastructure** | `core/src/infra/` | CacheManager + ReportGenerator |
| **Entry Points** | `core/src/skills/` | 19 skill `main.py` files, argument parsing + formatted output |

---

## Installation

### Prerequisites

```bash
pip install akshare pandas
```

### Option 1: Global Install (available to all OpenCode projects)

**Windows**:
```cmd
mklink /D "%USERPROFILE%\.config\opencode\skills\stock-analyzer" "C:\Users\Lenovo\Desktop\stock-analyzer-skills"
```

**Linux/macOS**:
```bash
ln -s /path/to/stock-analyzer-skills ~/.config/opencode/skills/stock-analyzer
```

### Option 2: Project-level Install

Copy the `.opencode/` directory to the target project root:

```bash
cp -r stock-analyzer-skills/.opencode /path/to/target-project/
```

### Option 3: Git Submodule (recommended for teams)

```bash
git submodule add <repo-url> .opencode/skills/stock-analyzer
```

---

## Configuration

All API keys and SMTP settings are managed in a single file:

```
.opencode/skills/core/src/config/.env
```

| Key | Description |
|-----|-------------|
| `TUSHARE_TOKEN` | Tushare Pro API token (financial/quotes/valuation) |
| `SMTP_HOST` / `SMTP_PORT` | Mail server address and port |
| `SMTP_USER` / `SMTP_PASSWORD` | Email credentials |
| `TAVILY_API_KEY` | Web Search API key |
| `OUTPUT_DIR` | Report output directory (default: `output/`) |

> **Note**: All skills share this config file. Changes take effect immediately.

---

## Usage

### OpenCode Invocation

Invoke skills directly in the OpenCode dialog:

```
skill(name="stock-analyzer")
skill(name="technical-analyzer")
skill(name="buffett-checklist")
skill(name="financial-analysis")
skill(name="roce-calculator")
skill(name="a-dividend-analyzer")
skill(name="percentile-analyzer")
skill(name="risk-analysis")
skill(name="shareholder-deep")
skill(name="valuation-anchor")
skill(name="market-analyzer")
skill(name="market-systemic-risk")
skill(name="industry-analysis")
skill(name="report-builder")
skill(name="email-sender")
skill(name="pdf-converter")
skill(name="akshare-docs")
skill(name="tushare-data")
skill(name="web-search")
skill(name="national-team-fund-tracker")
skill(name="darwinian_value_investing")
skill(name="munger_value_investing")
skill(name="cninfo-search")
skill(name="chronos-timeline")
```

### Command-line Usage

```bash
# Individual skill execution
python .opencode/skills/core/src/skills/stock-analyzer/main.py 600519
python .opencode/skills/core/src/skills/technical-analyzer/main.py 600519
python .opencode/skills/core/src/skills/buffett-checklist/main.py 600519
python .opencode/skills/core/src/skills/roce-calculator/main.py 600519
python .opencode/skills/core/src/skills/a-dividend-analyzer/main.py 600519
python .opencode/skills/core/src/skills/percentile-analyzer/main.py 600519
python .opencode/skills/core/src/skills/risk-analysis/main.py 600519
python .opencode/skills/core/src/skills/shareholder-deep/main.py 000651
python .opencode/skills/core/src/skills/valuation-anchor/main.py 600519
python .opencode/skills/core/src/skills/market-analyzer/main.py
python .opencode/skills/core/src/skills/market-systemic-risk/main.py
python .opencode/skills/core/src/skills/industry-analysis/main.py
python .opencode/skills/core/src/skills/email-sender/main.py "recipient" "subject" "body"
python .opencode/skills/core/src/skills/pdf-converter/main.py "file.pdf"
python .opencode/skills/core/src/skills/akshare-docs/main.py "stock_zh_a_spot"
python .opencode/skills/core/src/skills/web-search/main.py "query text"
python .opencode/skills/core/src/skills/national-team-fund-tracker/main.py
python .opencode/skills/core/src/skills/cninfo-search/main.py 600519
python .opencode/skills/core/src/skills/chronos-timeline/main.py 600519 回购
python .opencode/skills/core/src/skills/chronos-timeline/main.py 600338 锂矿 --relax --export-candidates cand.json
python .opencode/skills/core/src/skills/chronos-timeline/main.py --build-report annotated.json
```

---

## Scoring System

| Dimension | Max Score | Evaluation | Logic |
|-----------|:---------:|------------|-------|
| Profitability | 20 | ROCE absolute + trend | ROCE >20% → 20pts; drop >50% → -5pts |
| Financial Safety | 20 | Current ratio + debt ratio | CR >2 → +6pts; CR <0.5 → -6pts; debt <30% → +4pts |
| Valuation | 20 | PE level | PE <15 → 20pts; 15-25 → 15pts; 25-40 → 10pts; >40 → 5pts |
| Technicals | 20 | MA signal + RSI | Golden cross +5pts; Death cross -3pts; Oversold +3pts; Overbought -3pts |
| Business Outlook | 20 | Industry position + growth | Industry leader +10pts; High growth +10pts |
| News Risk | 20 | Negative news count | Integrity risk → 5pts; Business risk → 12pts; No risk → 20pts |

| Total | Rating | Suggestion |
|:-----:|:------:|------------|
| 80-100 | A Excellent | Active attention, consider buying |
| 65-79 | B Good | Sound fundamentals, buy on dips |
| 50-64 | C Average | Wait and see, bide time |
| 35-49 | D Poor | High risk, be cautious |
| 0-34 | E Dangerous | Avoid, too risky |

---

## Detailed Skill Descriptions

### roce-calculator

Calculates 10-year ROCE (Return on Capital Employed) for a stock.

**Formula**:
```
ROCE = EBIT / Capital Employed
Capital Employed = Total Assets - Current Liabilities
EBIT = Net Profit + Interest Expense + Income Tax
```

**ROCE Reference**:

| Range | Rating |
|-------|--------|
| > 20% | Excellent |
| 15% - 20% | Good |
| 10% - 15% | Average |
| < 10% | Poor |

### market-analyzer

Analyzes overall A-share market condition. No stock code required.

**Output**:
- Market-wide average PE ratio (Legu data)
- Shanghai Composite MA20 / MA50
- Bull/Bear signal: MA20 > MA50 → Bull | MA20 < MA50 → Bear

### stock-analyzer

Fetches real-time stock quotes and valuation data.

**Output**:
- Stock name / Industry / Current price / Change %
- PE(static/dynamic/TTM) / PB / Dividend yield(TTM)
- Market cap / EPS / Book value per share
- Buy/Sell suggestion based on PE and price change

### technical-analyzer

Analyzes stock technical indicators.

**Output**:
- **MA System**: MA50 / MA200 Golden cross (Bullish) or Death cross (Bearish)
- **RSI(14)**: >70 Overbought | <30 Oversold | 30-70 Neutral

### risk-analysis

Integrated risk control combining news risk assessment + historical percentile analysis.

**Risk Levels**:

| Level | Description |
|-------|-------------|
| 🔶 High Risk | Fraud, regulatory penalties, integrity issues, investigation |
| 🟡 Medium Risk | Earnings decline, shareholder减持, policy changes, exec resignation |
| 🟢 Low Risk | Normal operations, positive news |

### a-dividend-analyzer

Fetches historical dividend distribution details (stock splits, cash dividends, key dates).

**Output**:
- Historical dividend table with key dates
- Per-share metrics (capital reserve, undistributed profit, total shares)
- Dividend continuity analysis

### pdf-converter

Converts PDF files to Markdown format.

**Features**:
- PDF to Markdown
- Preserves tables and formatting
- Chart description extraction

### shareholder-deep

Deep shareholder analysis showing top 10 shareholders, institutional holdings, and insider trading.

**Output**:
- Top 10 tradable shareholders (last 5 periods)
- National team holdings (CSF, Huijin)
- Institutional/fund position changes
- Shareholder增减持 movements

### email-sender

Sends emails via SMTP protocol, supports attachments.

**Usage**:
```bash
python .opencode/skills/core/src/skills/email-sender/main.py "recipient" "subject" "body"
```

### buffett-checklist

Buffett 7-gate checklist. Aggregates data from 9 analyzers for independent evaluation across 7 gates.

**7 Gates**:
1. **Circle of Competence** — Do you understand the business? (8-point scale)
2. **Moat** — Does it have durable competitive advantage? (15-star scale)
3. **Management** — Is management trustworthy? (Red flag count)
4. **Financial Health** — 5 financial metric checks (pass count)
5. **Margin of Safety** — Is the price cheap enough? (5 criteria)
6. **Red Flags** — 7 deal-breaker checks
7. **Market Risk** — Is the market environment favorable? (20-point scale)

### financial-analysis

Deep financial analysis via Tushare API. 6-dimension scorecard + 4 red flag screens.

**Dimensions**: Profitability, Solvency, Efficiency, Growth, Cash Flow Quality, Dividend Returns

**Red Flags**: ROE<10%, Debt Ratio>70%, OCF/Net Profit<0.5, Goodwill/Equity>30%

> OpenCode only: `skill(name="financial-analysis")`

### percentile-analyzer

Historical percentile analysis. Calculates current price position in 3M/1Y/3Y/5Y history.

**Output**:
- Current/min/max/median prices per period
- Current percentile ranking
- Multi-period signal consistency

### report-builder

Full report generation. Coordinates 8 analysis skills using unified-template to produce a 10-chapter report.

**Chapters**: Market → Company → Industry → Financials → Shareholders → Valuation → Technicals → Risks → Score → Recommendations

### tushare-data

Tushare data research tool. Converts natural language queries into data fetch/clean/compare/export operations.

**Coverage**: A-share quotes, financials, valuations, fund flows, sectors/concepts

> OpenCode only: `skill(name="tushare-data")`

### national-team-fund-tracker

National team ETF monthly position tracking. Tracks share changes of 8 core broad-based ETFs heavily held by Huijin, reflecting the overall direction of national team market entry/exit.

**Output**:
- Monthly total trend (total shares curve)
- Per-ETF share change details
- MoM change direction
- Position structure analysis

**Usage**:
```bash
python .opencode/skills/core/src/skills/national-team-fund-tracker/main.py
```

### darwinian_value_investing

Evolutionary investing framework based on "Investing: The Last Liberal Art" by Parag Parikh. Translates core evolutionary concepts into actionable business ecosystem analysis and investment decision workflows.

> OpenCode only: `skill(name="darwinian_value_investing")`

### munger_value_investing

Charlie Munger value investing framework. Multi-dimensional data-driven stock evaluation system.

> OpenCode only: `skill(name="munger_value_investing")`

---

## Generated Reports

| Code | Name | Score | Rating | File |
|------|------|:-----:|:------:|------|
| 000651 | 格力电器 (Gree) | — | — | `output/格力电器_000651_综合分析报告.md` |
| 000651 | 格力电器 (Gree) | 5/6 pass+🟡neutral | Buy | Buffett Checklist (this session) |
| 000333 | 美的集团 (Midea) | 4/6 pass+🟡neutral | Buy | Buffett Checklist (this session) |

> Reports are saved in the `output/` directory and can be sent via email-sender.

---

## Data Sources

| Source | API / Function | Purpose |
|--------|---------------|---------|
| **Tushare Pro** | `pro.daily_basic()` / `pro.daily()` / `pro.stock_basic()` / `pro.fina_indicator()` | Valuation (PE/PB/DY/EPS/MCap/Industry) |
| **Sina Finance** | `akshare.stock_financial_report_sina()` | Financial statements |
| **Sina Finance** | `akshare.stock_zh_a_daily()` | Historical K-line data |
| **East Money** | `akshare.stock_news_em()` | Stock news |
| **East Money** | `akshare.stock_fhps_detail_em()` | Dividend data |
| **Legu** | `akshare.stock_market_pe_lg()` | Market-wide PE |
| **Sina** | `akshare.stock_zh_index_daily()` | Shanghai Composite index |

---

## Notes

### Code of Conduct (All Skills)
1. **Ambiguity must be clarified**: When requirements are unclear, ask the user — never make assumptions
2. **No擅自 assumptions**: Always confirm with the user before proceeding
3. **Show findings first**: Present key findings before generating a full report
4. **Core code changes require confirmation**: Modifications to `core/src/analyzers/`, `core/src/skills/`, `core/__init__.py` must be presented to the user with plan and impact before execution

---

1. **Tushare Pro replaces Xueqiu**: `StockAnalyzer.get_stock_profile()` uses Tushare Pro for PE/PB/DY
2. **East Money instability**: `stock_zh_a_spot_em()` and `stock_zh_a_hist()` frequently timeout — prefer Sina and Tushare
3. **Chinese column names**: Sina returns Chinese column names; uses `safe_get_col()` for fuzzy matching internally
4. **Slow ROCE calculation**: Requires fetching financial statements year by year (2 tables/year, 20+ requests for 10 years)
5. **News filtering**: Broad market news (sector/concept/fund flow) excluded from individual stock risk assessment
6. **Network dependency**: All data from online APIs; some have rate limits (recommend >3s intervals)

---

## FAQ

**Q: "ModuleNotFoundError: No module named 'core'" on run?**  
A: Run from the project root. `main.py` automatically adds 4 parent directories to `sys.path` to import `core`. Always execute from the project root.

**Q: "Expecting value: line 1 column 1" error in financial analysis?**  
A: Sina Finance occasionally returns non-JSON responses. Retry later.

**Q: ROCE calculation is slow?**  
A: ROCE needs year-by-year financial statements (2 tables/year). 10 years = 20+ requests, please be patient.

**Q: How to add new analysis dimensions?**  
A: Create a new Analyzer class in `core/src/analyzers/`, add wrapper function in `core/__init__.py`, then call it from the skill's `main.py`.

---

## License

MIT
