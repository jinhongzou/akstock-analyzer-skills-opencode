---
name: chronos-timeline
description: CHRONOS 事件追踪分析。追踪特定事件的完整演变过程（如"回购"事件从预案到完成的来龙去脉），输入股票代码+事件关键词，输出 HTML 时间线报告
---

# CHRONOS 事件追踪分析

**核心功能**: 追踪 A 股上市公司**特定事件**的完整演变过程。输入股票代码 + 事件关键词（如"回购""利润分配""人事变动"），自动采集相关公告和新闻，构建该事件从萌芽到结束的完整时间线，识别发展阶段，评估事件完整性。

**数据源**: 巨潮资讯网公告（主）+ 东方财富新闻（补）
**无需 API Key**: 全部使用公开接口

---

## 框架架构

```
chronos-timeline/
├── SKILL.md                         # 总入口（本文件）
├── guides/
│   ├── 01-per-event-analysis.md     # 第〇步：逐事件影响评估
│   ├── 02-completeness-check.md     # 第一步：事件完整性检查
│   ├── 03-stage-structure.md        # 第二步：检查阶段结构合理性
│   ├── 04-event-density.md          # 第三步：事件密度分析
│   └── 05-overall-rating.md         # 第四步：综合评级
└── core/src/skills/chronos-timeline/
    └── main.py                      # 数据采集 + HTML 生成
```

---

## 使用方式

**OpenCode 调用**:
```
skill(name="chronos-timeline")
```

**命令行运行**:
```bash
python .opencode/skills/core/src/skills/chronos-timeline/main.py <股票代码> <事件关键词> [天数] [选项]
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `股票代码` | 必填。如 `600519` 或 `000651` | - |
| `事件关键词` | 必填。你想追踪的具体事件，如 `回购`、`利润分配`、`人事变动` | - |
| `天数` | 可选，回溯天数 | 1825（约5年） |
| `--relax` | 宽松匹配模式，将关键词拆为单字匹配，最大化召回候选 | 关闭 |
| `--export-candidates FILE` | 导出候选事件为 JSON，供 AI 语义标注（跳过 HTML 生成） | 无 |
| `--build-report FILE` | 从 AI 标注的 JSON 重建 HTML 报告（跳过数据采爬） | 无 |

### 使用示例

```bash
# 基本用法（严格关键词匹配）
python .opencode/skills/core/src/skills/chronos-timeline/main.py 600519 回购
python .opencode/skills/core/src/skills/chronos-timeline/main.py 600519 利润分配
python .opencode/skills/core/src/skills/chronos-timeline/main.py 600519 增持 365

# AI 辅助语义匹配工作流
python .opencode/skills/core/src/skills/chronos-timeline/main.py 600338 锂矿 --relax --export-candidates cand.json   # 宽松匹配，导出候选
# → AI 标注 cand.json（标记 relevant/analysis 字段）→ 保存为 annotated.json
python .opencode/skills/core/src/skills/chronos-timeline/main.py --build-report annotated.json                     # 从标注构建 HTML
```

输出为交互式 HTML 报告，保存在 `output/` 目录下。

---

## 核心逻辑

### 事件阶段体系

事件按发展阶段分为 4 个阶段，由标题关键词自动判定：

| 阶段 | 标签 | 关键词（命中任意一个即判定） | 含义 |
|------|------|-----------------------------------|------|
| 📋 **预备期** | `预备期` | 拟、预案、计划、提议、意向、通知、召集、筹划、论证、考虑、研究、准备、草案、征求意见 | 事件首次被提出或公告 |
| 🔧 **实施期** | `实施期` | 实施、执行、进行中、进展、调整、变更、修订、修改、审议、通过、批准、同意、授权、方案 | 事件正在执行或决策中 |
| ✅ **完成期** | `完成期` | 完成、结果、报告、结束、终止、注销、交割、过户 | 事件收尾或结束 |
| 📌 **其他** | `其他` | 以上都不匹配 | 补充报道、评论、无法识别阶段的事件 |

---

## HTML 报告结构

报告保存在 `output/{股票代码}_{关键词}_chronos.html`，包含以下模块：

| 模块 | 内容 |
|------|------|
| 事件概览 | 事件总数、公告/新闻数、各阶段统计卡片 |
| 年度分布 | 每年事件数柱状图，识别活跃年份 |
| 事件时间线 | 时间升序排列，每事件标注阶段 + 原文链接 + 内容摘要 + AI 评估占位区 |
| 阶段过滤 | 按预备期/实施期/完成期/其他 筛选事件 |
| 事件摘要 | 追踪关键词、时间跨度、阶段分布、最早/最近事件 |

---

## AI 辅助语义匹配工作流

当用户输入的关键词与公告标题用词不匹配（如用户说"锂矿"但公告写"阿根廷孙公司环评进展"）时，可通过以下 AI 辅助流程解决语义鸿沟：

```
用户输入 "西藏珠峰 锂矿"
    │
    ├─ 问题：关键词"锂矿"在公告标题中匹配不到（标题写的是"实控阿根廷孙公司环评进展"）
    │
    ├─ Step 1: 用宽泛关键词（如"阿根廷"）导出候选事件
    │   └─ python main.py 600338 阿根廷 --export-candidates cand.json
    │
    ├─ Step 2: AI 逐条语义判断相关性 + 逐事件分析
    │   ├─ 判断每条候选是否与用户关心的主题相关
    │   ├─ 对相关事件标注影响角色、方向、程度
    │   └─ 保存为 annotated.json
    │
    └─ Step 3: 从标注构建 HTML 报告
        └─ python main.py --build-report annotated.json
```

### JSON 标注格式

```json
{
  "stock_code": "600338",
  "stock_name": "西藏珠峰",
  "keyword": "锂矿",
  "days": 1825,
  "events": [
    {
      "seq": 1,
      "date": "2024-07-02",
      "source": "公告",
      "title": "关于公司实控阿根廷孙公司取得环评批复的公告",
      "url": "http://static.cninfo.com.cn/finalpage/...PDF",
      "content": "",
      "stage": "完成期",
      "relevant": true,
      "analysis": "[关键里程碑] 历经近两年审批...影响：正面 - 重大 - 扫清法律障碍"
    }
  ]
}
```

| 字段 | 说明 | 由谁填写 |
|------|------|---------|
| `relevant` | `true`=相关，`false`=不相关（不相关的事件不会出现在最终报告） | AI |
| `analysis` | 逐事件评估文本，将注入 HTML 的 AI 评估区 | AI |
| `stage` | 如果 AI 想覆盖自动阶段判定，可在此指定 | AI（可选） |

### 宽松匹配（`--relax`）

当严格关键词匹配结果为 0 时：
1. 先用 `--relax` 模式扩大召回（字符级匹配）
2. 若仍为 0，考虑用更宽泛的关键词（如公司名、项目名、地名）重新采集
3. 导出 JSON 后由 AI 做语义过滤

---

## 分析工作流 Todo 清单

### ▷ 标准模式（关键词精准匹配）

- [ ] **运行脚本** — `python main.py <股票代码> <关键词> [天数]`，生成 HTML 报告
- [ ] **打开 HTML** — 在浏览器中打开 `output/{股票代码}_{关键词}_chronos.html`
- [ ] **逐事件分析** — 点击原文链接阅读完整内容，将评估填入 AI 评估区
- [ ] **整体评估** — 依次按 4 步指南完成完整性/阶段/密度/综合评级

### ▷ AI 辅助模式（语义匹配 + 自动分析）

- [ ] **导出候选** — `python main.py <代码> <关键词> --relax --export-candidates cand.json`
- [ ] **AI 标注** — 逐条判断 `relevant`、填写 `analysis`，保存为 JSON
- [ ] **构建报告** — `python main.py --build-report annotated.json`
- [ ] **复核并补充整体评估** — 打开 HTML 按 4 步指南完成整体评级

---

## 每个事件的可操作元素

HTML 中每条事件包含以下可操作元素：

| 要素 | 说明 | 你的操作 |
|------|------|---------|
| **标题链接** 🔗 | 标题为可点击链接（公告→PDF，新闻→东方财富原文） | 点击查看完整原文内容 |
| **原文按钮** 🔗 | 事件右上角的 "🔗 原文" 按钮 | 同上，到原文的快捷入口 |
| **内容摘要** | 新闻事件有灰色分隔线 + 正文摘要（>200字截断） | 快速浏览事件要点 |
| **AI 评估区** | 紫色背景左边框，初始显示 "`[AI评估待补充]`" | 将占位文本替换为你的分析（见下方替换方法） |

代码**只提供原始数据和可跳转链接**，不包含任何分析判断。逐事件的影响评估由你独立完成。

---

## 程序化替换 AI 评估占位符 ⭐ 关键操作

HTML 报告中每条事件的 AI 评估区使用 **固定的占位符字符串**，便于你通过代码进行批量替换。

### 占位符精确字符串

每条事件的 `analysis-placeholder` div 内部包含以下固定文本（**所有事件完全相同**，不因关键词而变）：

```
[AI评估待补充] 点击原文链接阅读后，在此填入你的分析
```

> **为什么固定字符串重要**：之前版本中占位符包含 `分析此事件对「{keyword}」整体发展的影响`，导致不同关键词生成不同字符串，`str.replace()` 无法精准匹配。新版本统一为固定字符串，确保替换零失败。

### Python 批量替换（整批相同内容）

将所有事件填入同一分析（适用于需要先统一填写的情况）：

```python
with open("output/600338_阿根廷_chronos.html", "r", encoding="utf-8") as f:
    html = f.read()

my_assessment = "[关键里程碑] 你的分析内容。影响：正面 - 重大 - 关联说明"
html = html.replace(
    "[AI评估待补充] 点击原文链接阅读后，在此填入你的分析",
    my_assessment
)

with open("output/600338_阿根廷_chronos.html", "w", encoding="utf-8") as f:
    f.write(html)
```

### Python 逐事件替换（每条不同分析）

利用 `data-seq` 属性精确定位每条事件，填入不同的分析内容：

```python
import re

with open("output/600338_阿根廷_chronos.html", "r", encoding="utf-8") as f:
    html = f.read()

assessments = {
    1: "[常规进展] 你的分析。影响：中性 - 轻微 - 关联说明",
    2: "[触发信号] 你的分析。影响：负面 - 重大 - 关联说明",
    # ... 按 seq 编号依次填写全部事件
}

# ⚠️ 必须从右向左替换，因为 rfind 从末尾开始查找
placeholder = "[AI评估待补充] 点击原文链接阅读后，在此填入你的分析"

for seq in sorted(assessments.keys(), reverse=True):
    idx = html.rfind(placeholder)
    if idx >= 0:
        html = html[:idx] + assessments[seq] + html[idx + len(placeholder):]

with open("output/600338_阿根廷_chronos.html", "w", encoding="utf-8") as f:
    f.write(html)
```

### 替换格式建议

推荐的评估文本格式（与 `guides/01-per-event-analysis.md` 保持一致）：

```
[事件角色] 评估摘要。影响：影响方向 - 影响程度 - 关联说明
```

示例：

```
[关键里程碑] 环评获批，经历近两年审批终于获得环保批复，是整个项目最重大的里程碑。影响：正面 - 重大 - 为后续建设扫清法律障碍，但时间成本已很高
```

---

## 常用事件关键词参考

| 关键词 | 追踪内容 | 典型生命周期 |
|--------|---------|-------------|
| `回购` | 股份回购事件 | 预案→实施进展→完成注销 |
| `利润分配` | 分红送配事件 | 预案→股东大会通过→实施公告 |
| `人事变动` | 高管变更事件 | 辞职→提名→选举→聘任 |
| `增持` / `减持` | 股东增减持事件 | 计划→进展→完成 |
| `质押` | 股权质押事件 | 质押→补充质押→解质押 |
| `投资` | 对外投资事件 | 意向→决议→实施 |
| `合同` | 重大合同事件 | 中标/签约→履行→完成 |
| `股权激励` | 股权激励事件 | 方案→授予→解锁 |

---

## 数据源说明

| 数据源 | 接口 | 覆盖范围 | 优先级 |
|--------|------|---------|--------|
| 巨潮资讯网 | `cninfo.com.cn` 官方 API | 5 年公告 | 主源 |
| 东方财富 | 搜索 API | 近期新闻（受限流影响） | 补充 |

---

## 相关指南文件

- [01-per-event-analysis.md](guides/01-per-event-analysis.md) — 逐事件影响评估
- [02-completeness-check.md](guides/02-completeness-check.md) — 事件完整性检查
- [03-stage-structure.md](guides/03-stage-structure.md) — 阶段结构检查
- [04-event-density.md](guides/04-event-density.md) — 事件密度分析
- [05-overall-rating.md](guides/05-overall-rating.md) — 综合评级

---

## 清理输出文件

每次运行 `main.py` 会生成一个 HTML 报告文件，保存在项目根目录的 `output/` 目录下：

```
output/{股票代码}_{关键词}_chronos.html
```

### 清理建议

| 场景 | 操作 |
|------|------|
| **分析完成后** | 建议清理此次分析过程产生的临时文件 |

> **注意**：`output/` 目录也用于其他 Skill 的输出文件（如 report-builder）。

---

## 免责声明

本分析仅供研究参考，不构成投资建议。事件数据基于公开信息的关键词匹配。标准模式下不含 LLM 分析；AI 辅助模式下语义标注由外层 AI 完成，生成工具本身不含分析逻辑。
