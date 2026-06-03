---
name: cninfo-search
description: 巨潮资讯网公告搜索。通过 cninfo.com.cn 官方API查询A股上市公司公告，支持按名称/代码搜索、日期范围过滤、公告类别筛选、PDF下载链接获取
---

# Cninfo Search

**功能**: 查询巨潮资讯网（cninfo.com.cn）上市公司公告，获取公告标题、发布时间、PDF下载链接
**数据源**: cninfo.com.cn 官方信息披露 API
**无需 API Key**: 直接调用巨潮资讯网公开接口，永久有效的 PDF 下载链接

---

## 使用方式

**OpenCode 调用**:
```
skill(name="cninfo-search")
```

**命令行运行**:
```bash
python .opencode/skills/core/src/skills/cninfo-search/main.py <股票代码或公司名称> [选项]
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `股票代码或名称` | 必填。如 `600519` 或 `贵州茅台` | - |
| `--from` | 起始日期 (YYYY-MM-DD) | 不限 |
| `--to` | 截止日期 (YYYY-MM-DD) | 不限 |
| `--page` | 页码 | 1 |
| `--size` | 每页条数 (最大50) | 20 |
| `--plate` | 板块: sh(沪市)/sz(深市)/bj(北交所) | 自动 |
| `--category` | 公告类别编码 | 不限 |
| `--pdf` | 显示PDF完整链接 | 只显示PDF文件名 |
| `--full` | 显示全部字段（含类别编码、orgId等） | 否 |

### 示例

```bash
# 按股票代码搜索
python .opencode/skills/core/src/skills/cninfo-search/main.py 600519

# 按公司名称搜索
python .opencode/skills/core/src/skills/cninfo-search/main.py 贵州茅台

# 指定日期范围 + 显示PDF链接
python .opencode/skills/core/src/skills/cninfo-search/main.py 西藏珠峰 --from 2026-04-01 --to 2026-04-30 --pdf

# 指定板块 + 翻页
python .opencode/skills/core/src/skills/cninfo-search/main.py 金戈新材 --plate bj --page 1 --size 30

# 显示全部详细信息
python .opencode/skills/core/src/skills/cninfo-search/main.py 格力电器 --full

# 新三板代码查询（查询原新三板时期的历史公告）
python .opencode/skills/core/src/skills/cninfo-search/main.py 873524
```

---

## 输出字段说明

| 字段 | 说明 |
|------|------|
| 股票代码 | 上市公司代码（如 600519） |
| 公司名称 | 上市公司简称 |
| 公告标题 | 公告完整标题 |
| 公告日期 | 发布日期 |
| PDF链接 | 公告PDF文件链接（永久有效） |
| 公告类型编码 | 内部类型分类代码 |
| orgId | 公司机构ID |

---

## 注意事项

1. **股票代码参数**：系统自动识别代码（纯数字）vs 公司名称（含中文），分别用不同方式查询
2. **搜索方式**：
   - 输入纯数字代码 → 先用 stock 参数精确匹配，匹配失败后自动切换到名称搜索
   - 输入公司名称 → 直接用 searchkey 参数模糊匹配
3. **公告 PDF** 存储在 `http://static.cninfo.com.cn/` 永久 CDN，链接永久有效，无需认证即可下载
4. **分页限制**：API 最多返回前 100 页数据，建议缩小日期范围获得精确结果
5. **请求间隔**：建议每次请求间隔 >1 秒，避免触发频率限制
6. **数据合规**：巨潮资讯网是证监会指定信息披露平台，本工具仅用于个人投资研究

---

## 公告类别编码参考（用于 --category 参数）

| 编码 | 类别 |
|------|------|
| category_010301 | 年度报告 |
| category_010302 | 半年度报告 |
| category_010303 | 季度报告 |
| category_011301 | 利润分配/分红 |
| category_011901 | 股东大会 |
| category_011501 | 董事会决议 |
| category_011701 | 交易/投资 |
| category_011513 | 股份回购 |
| category_011711 | 对外担保 |
| category_012103 | 异常波动 |
| category_012301 | 股权变动 |
| category_012305 | 会计政策变更 |
| category_012303 | 人事变动 |
| category_0125 | 风险提示 |
| category_012399 | 其他重大事项 |

---

## ⭐ 你的评估任务：公告信息评估框架（必须执行）

> main.py 只输出原始数据。你必须基于以下框架独立评估公告信息。

### 评估维度

| # | 维度 | 数据来源 | 评估内容 |
|---|------|---------|---------|
| 1 | **公告重要性** | 公告标题 | 根据标题判断是否为重大事项（年报/资产重组/分红/异常波动等为重大；日常管理制度/人事任免等为常规） |
| 2 | **时间紧迫性** | 公告日期 | 近期公告（1周内）需要重点关注；超过1个月的逐步淡化 |
| 3 | **信号方向** | 公告标题 | 正面信号（业绩预增/分红/回购/合同签署）vs 负面信号（亏损/诉讼/减持/违规/异常波动） |
| 4 | **PDF阅读建议** | PDF链接 | 判断是否需要下载PDF细读（年报/重组/重大合同等重要公告建议阅读原文） |

### 评估输出格式

对每份公告输出信号标签：
- **🔴 重大/负面**：异常波动、违规处罚、诉讼仲裁、业绩亏损、退市风险
- **🟡 关注**：股权变动、人事变更、担保、关联交易、募资
- **🟢 正面**：业绩预增、分红方案、股份回购、重大合同、资产注入
- **⚪ 常规**：日常经营、制度文件、会议通知（通常无需细读）

### 综合研判

评估完成后，汇总关键发现：
1. 近期有哪些需要重点关注的重要公告？
2. 是否存在负面信号/风险提示？
3. 哪些公告建议下载PDF原文细读？
4. 整体信息面评估：积极/中性/消极

---

## 依赖安装

```bash
pip install requests
```

---

## 相关资源

- 巨潮资讯网: https://www.cninfo.com.cn
- API 端点: `POST http://www.cninfo.com.cn/new/hisAnnouncement/query`
- PDF CDN: `http://static.cninfo.com.cn/`
