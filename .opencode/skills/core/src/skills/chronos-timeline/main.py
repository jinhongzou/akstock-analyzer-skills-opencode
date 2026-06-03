# -*- coding: utf-8 -*-
"""
CHRONOS 事件追踪分析（chronos-timeline）

针对特定事件关键词的追踪工具。
接受 股票代码 + 事件关键词，追踪该事件在公告/新闻中的完整时间线。

核心流程:
  事件采集 ──→ 关键词过滤 ──→ 时间线构建（阶段标注）──→ HTML 时间线输出

数据源:
  - 公告: 巨潮资讯网 cninfo（主源，覆盖 5 年）
  - 新闻: 东方财富（补充源）

注意: 纯事件维度分析，不含任何股价数据。
"""
import sys
import os
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import akshare as ak
import pandas as pd
import requests


# ============================================================
# 常量
# ============================================================
DEFAULT_DAYS = 1825  # 约 5 年
CNINFO_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

_IMPORTANT_CATEGORIES = [
    "category_010301",   # 年报
    "category_010302",   # 半年报
    "category_010303",   # 季报
    "category_011301",   # 分红
    "category_011701",   # 股权出售/收购
    "category_012103",   # 异常波动
    "category_012399",   # 其他重大事项
    "category_010913",   # 业绩预告
    "category_010914",   # 业绩快报
]

# 事件阶段关键词
_STAGE_RULES = [
    {
        "stage": "预备期",
        "keywords": ["拟", "预案", "计划", "提议", "意向", "通知", "召集",
                      "筹划", "论证", "考虑", "研究", "准备", "草案", "征求意见"],
        "priority": 1,
    },
    {
        "stage": "实施期",
        "keywords": ["实施", "执行", "进行中", "进展", "调整", "变更", "修订", "修改",
                      "审议", "通过", "批准", "同意", "授权", "方案"],
        "priority": 2,
    },
    {
        "stage": "完成期",
        "keywords": ["完成", "结果", "报告", "结束", "终止", "注销", "交割", "过户"],
        "priority": 3,
    },
]


# ============================================================
# 工具函数
# ============================================================

def get_stock_name(stock_code: str) -> str:
    """通过新浪接口获取股票中文名称"""
    prefix = "sh" if stock_code.startswith("6") else "sz"
    url = f"https://hq.sinajs.cn/list={prefix}{stock_code}"
    try:
        r = requests.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=5)
        text = r.text.strip()
        if "=" in text:
            content = text.split("=", 1)[1].strip().strip('"').strip("'")
            name = content.split(",")[0].strip()
            if name:
                return name
    except Exception:
        pass
    return stock_code


def truncate(text: str, max_len: int = 80) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


def _escape_html(text) -> str:
    if text is None:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ============================================================
# 事件采集
# ============================================================

CNINFO_PDF_BASE = "http://static.cninfo.com.cn/"


def get_cninfo_data(stock_code: str, days: int) -> list:
    """获取巨潮资讯网公告。返回 list of dict: {date, source, title, category, url}"""
    start_dt = datetime.now() - timedelta(days=days)
    from_date = start_dt.strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")
    items = []

    CNINFO_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://www.cninfo.com.cn/new/index",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    for page in range(1, 21):
        params = {
            "pageNum": str(page),
            "pageSize": "30",
            "seDate": f"{from_date}~{to_date}",
            "isHLtitle": "true",
            "sord": "date",
            "order": "desc",
            "searchkey": stock_code,
        }
        try:
            resp = requests.post(CNINFO_URL, data=params, headers=CNINFO_HEADERS, timeout=15)
            data = resp.json()
            announcements = data.get("announcements")
            if not announcements:
                break
            for ann in announcements:
                ts = ann.get("announcementTime", 0)
                if not ts:
                    continue
                date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                try:
                    pub_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if pub_date < start_dt:
                        continue
                except ValueError:
                    continue
                title = ann.get("announcementTitle", "").replace("<em>", "").replace("</em>", "")
                category = str(ann.get("categoryCode", ""))
                # 构建 PDF 原文链接
                adjunct_url = ann.get("adjunctUrl", "")
                pdf_url = CNINFO_PDF_BASE + adjunct_url if adjunct_url else ""
                items.append({
                    "date": date_str,
                    "source": "公告",
                    "title": title,
                    "category": category,
                    "url": pdf_url,
                })
            time.sleep(0.3)
        except Exception:
            break

    seen = set()
    deduped = []
    for i in items:
        key = (i["date"], i["title"])
        if key not in seen:
            seen.add(key)
            deduped.append(i)
    deduped.sort(key=lambda x: x["date"], reverse=True)
    return deduped


def _fetch_news_page(search_key: str, page: int) -> list:
    """调用东方财富搜索 API 获取单页新闻"""
    url = "https://search-api-web.eastmoney.com/search/jsonp"
    inner_param = {
        "uid": "",
        "keyword": search_key,
        "type": ["cmsArticleWebOld"],
        "client": "web",
        "clientType": "web",
        "clientVersion": "curr",
        "param": {
            "cmsArticleWebOld": {
                "searchScope": "default",
                "sort": "default",
                "pageIndex": page,
                "pageSize": 50,
                "preTag": "<em>",
                "postTag": "</em>",
            }
        },
    }
    params = {
        "cb": "jQuery_cb",
        "param": json.dumps(inner_param, ensure_ascii=False),
        "_": "1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"https://so.eastmoney.com/news/s?keyword={search_key}",
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        text = r.text
        start = text.index("(") + 1
        end = text.rindex(")")
        data = json.loads(text[start:end])
        rows = data.get("result", {}).get("cmsArticleWebOld", [])
        return rows
    except Exception:
        return []


def get_news_data(stock_code: str, days: int, stock_name: str = "") -> list:
    """获取东方财富新闻。返回 list of dict: {date, source, title, url, content}"""
    start_dt = datetime.now() - timedelta(days=days)
    seen_titles = set()
    items = []

    company_kw = [stock_code]
    if stock_name and stock_name != stock_code:
        core_name = stock_name.replace("股份有限公司", "").replace("有限责任公司", "").replace("有限公司", "").strip()
        if core_name:
            company_kw.append(core_name)
        company_kw.append(stock_name)

    years = set()
    for y in range(start_dt.year, datetime.now().year + 1):
        years.add(str(y))
    search_keys = [stock_code] + [f"{stock_code} {y}" for y in sorted(years)]

    for search_key in search_keys:
        for page in range(1, 11):
            rows = _fetch_news_page(search_key, page)
            if not rows:
                break
            has_recent = False
            for row in rows:
                title = str(row.get("title", "")).strip()
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)
                date_str = str(row.get("date", ""))[:10]
                try:
                    pub_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
                if pub_date < start_dt or pub_date > datetime.now():
                    continue
                has_recent = True
                if company_kw and not any(kw in title for kw in company_kw):
                    continue
                # 去除 API 返回的 <em> 高亮标签
                title_clean = title.replace("<em>", "").replace("</em>", "")
                raw_content = row.get("content", "")
                content_clean = raw_content.replace("<em>", "").replace("</em>", "") if raw_content else ""
                # 原文链接和内容摘要
                article_url = row.get("url", "")
                items.append({
                    "date": date_str,
                    "source": "新闻",
                    "title": title_clean,
                    "url": article_url,
                    "content": content_clean,
                })
            if not has_recent:
                break
        time.sleep(0.5)

    items.sort(key=lambda x: x["date"], reverse=True)
    return items


# ============================================================
# 关键词过滤
# ============================================================

def filter_by_keyword(items: list, keyword: str) -> list:
    """
    根据关键词过滤事件。
    keyword 可以是单个词或多个词（用空格分隔，满足任意一个即匹配）。
    """
    keywords = [k.strip() for k in keyword.split() if k.strip()]
    if not keywords:
        return items

    result = []
    seen = set()
    for item in items:
        title = item["title"]
        # 去重
        key = (item["date"], title)
        if key in seen:
            continue
        seen.add(key)
        # 关键词匹配
        if any(kw in title for kw in keywords):
            result.append(item)
    return result


def filter_by_keyword_relaxed(items: list, keyword: str) -> list:
    """
    宽松关键词匹配：将关键词拆分为单个非空格字符，
    标题中包含任一字符即匹配（最大化召回，供后续 AI 语义筛选）。
    """
    chars = [c for c in keyword if c.strip()]
    if not chars:
        return items

    result = []
    seen = set()
    for item in items:
        title = item["title"]
        key = (item["date"], title)
        if key in seen:
            continue
        seen.add(key)
        if any(c in title for c in chars):
            result.append(item)
    return result


# ============================================================
# 阶段检测
# ============================================================

def detect_stage(title: str) -> str:
    """
    根据标题关键词检测事件所处阶段。
    返回: 预备期 / 实施期 / 完成期 / 其他
    """
    matched = []
    for rule in _STAGE_RULES:
        for kw in rule["keywords"]:
            if kw in title:
                matched.append((rule["priority"], rule["stage"]))
                break
    if matched:
        matched.sort(key=lambda x: x[0])
        return matched[0][1]
    return "其他"


# ============================================================
# 时间线构建
# ============================================================

def build_timeline(events: list) -> list:
    """
    构建事件时间线。
    - 按时间升序排列
    - 标注阶段
    - 标注序号
    """
    sorted_events = sorted(events, key=lambda x: x["date"])
    for idx, ev in enumerate(sorted_events, 1):
        ev["seq"] = idx
        ev["stage"] = detect_stage(ev["title"])
    return sorted_events


# ============================================================
# 统计
# ============================================================

def compute_stats(timeline: list, keyword: str) -> dict:
    """计算事件统计摘要"""
    total = len(timeline)
    news_count = sum(1 for e in timeline if e["source"] == "新闻")
    ann_count = sum(1 for e in timeline if e["source"] == "公告")

    # 分阶段统计
    stage_counts = defaultdict(int)
    for e in timeline:
        stage_counts[e["stage"]] += 1

    # 按年/月统计
    year_counts = defaultdict(int)
    month_counts = defaultdict(int)
    for e in timeline:
        y = e["date"][:4]
        m = e["date"][:7]
        year_counts[y] += 1
        month_counts[m] += 1

    # 时间跨度
    dates = sorted(e["date"] for e in timeline)
    time_span = f"{dates[0]} ~ {dates[-1]}" if len(dates) >= 2 else dates[0] if dates else ""

    return {
        "total": total,
        "news_count": news_count,
        "ann_count": ann_count,
        "keyword": keyword,
        "stage_counts": dict(stage_counts),
        "year_counts": dict(year_counts),
        "month_counts": dict(month_counts),
        "time_span": time_span,
    }


# ============================================================
# JSON 导出 / 构建
# ============================================================

def export_candidates_json(timeline: list, filepath: str,
                           stock_code: str, stock_name: str,
                           keyword: str, days: int):
    """导出候选事件为 JSON，供外层 AI 语义标注"""
    data = {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "keyword": keyword,
        "days": days,
        "events": timeline,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → 候选事件已导出: {filepath}")
    print(f"  → 共 {len(timeline)} 条，请用 AI 标注相关性和分析后执行 --build-report")


def build_report_from_annotated(annotated_path: str):
    """从 AI 标注的 JSON 重建 HTML 报告"""
    with open(annotated_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    stock_code = data["stock_code"]
    stock_name = data["stock_name"]
    keyword = data["keyword"]
    days = data["days"]

    # 仅保留 AI 判定为相关的事件
    relevant = [e for e in data["events"] if e.get("relevant", False)]
    if not relevant:
        print("❌ 标注数据中没有相关事件。")
        sys.exit(0)

    # 按时间升序排列，重新编号
    relevant.sort(key=lambda x: x["date"])
    analysis_map = {}
    for idx, ev in enumerate(relevant, 1):
        ev["seq"] = idx
        if not ev.get("stage"):
            ev["stage"] = detect_stage(ev["title"])
        if ev.get("analysis"):
            analysis_map[idx] = ev["analysis"]

    timeline = relevant
    stats = compute_stats(timeline, keyword)

    # 生成 HTML（注入 AI 分析）
    html = format_html_report(
        stock_code, stock_name, keyword, days, timeline, stats,
        analysis_map=analysis_map,
    )

    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    safe_keyword = keyword.replace("/", "_").replace("\\", "_").replace(" ", "_")
    filepath = os.path.join(output_dir, f"{stock_code}_{safe_keyword}_chronos.html")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📄 HTML 报告已生成")
    print(f"   → {filepath}")
    print("声明: 本分析仅供参考，不构成投资建议。")


# ============================================================
# HTML 输出
# ============================================================

def format_html_report(stock_code: str, stock_name: str, keyword: str,
                       days: int, timeline: list, stats: dict,
                       analysis_map: dict = None) -> str:
    """
    生成事件追踪 HTML 报告。
    - 只展示匹配关键词的事件时间线
    - 按时间升序排列
    - 标注阶段
    """
    stock_name_display = f"{stock_name} ({stock_code})" if stock_name != stock_code else stock_code
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 阶段颜色
    stage_colors = {
        "预备期": {"bg": "rgba(96,165,250,0.2)", "text": "#60a5fa", "dot": "#60a5fa"},
        "实施期": {"bg": "rgba(251,191,36,0.2)", "text": "#fbbf24", "dot": "#fbbf24"},
        "完成期": {"bg": "rgba(52,211,153,0.2)", "text": "#34d399", "dot": "#34d399"},
        "其他":   {"bg": "rgba(148,163,184,0.15)", "text": "#94a3b8", "dot": "#94a3b8"},
    }

    stage_icons = {
        "预备期": "📋",
        "实施期": "🔧",
        "完成期": "✅",
        "其他": "📌",
    }

    # 构建事件 JSON（给 JS 用）
    events_json = []
    for e in timeline:
        events_json.append({
            "seq": e["seq"],
            "date": e["date"],
            "source": e["source"],
            "title": _escape_html(e["title"]),
            "stage": e.get("stage", "其他"),
            "url": e.get("url", ""),
            "content": _escape_html(e.get("content", "")),
        })

    # 统计卡片
    stage_cards = ""
    for stage in ["预备期", "实施期", "完成期", "其他"]:
        count = stats["stage_counts"].get(stage, 0)
        if count == 0 and stage == "其他":
            continue
        colors = stage_colors.get(stage, stage_colors["其他"])
        icon = stage_icons.get(stage, "📌")
        # 如果某阶段为 0 且不是"其他"，也显示
        stage_cards += f"""
            <div class="stat-card" style="border-top:3px solid {colors['dot']};">
                <div class="stat-value" style="color:{colors['text']};">{count}</div>
                <div class="stat-label">{icon} {stage}</div>
            </div>"""

    # 年分布
    year_bar_parts = []
    if stats["year_counts"]:
        max_year_count = max(stats["year_counts"].values())
        for y in sorted(stats["year_counts"].keys()):
            c = stats["year_counts"][y]
            pct = c / max_year_count * 100 if max_year_count else 0
            year_bar_parts.append(
                f'<div style="flex:1;text-align:center;font-size:11px;color:#64748b;">'
                f'<div style="background:#6366f1;height:{pct:.0f}px;max-height:60px;border-radius:4px 4px 0 0;'
                f'margin:0 2px;" title="{y}: {c}条"></div>'
                f'<span>{y}</span><br><span style="font-weight:600;color:#e2e8f0;">{c}</span>'
                f'</div>'
            )

    year_bar_html = "".join(year_bar_parts) if year_bar_parts else ""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CHRONOS 事件追踪 - {stock_name_display} #{keyword}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #0f172a; color: #e2e8f0; line-height: 1.6; }}

.header {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 32px 24px; border-bottom: 1px solid #334155; }}
.header h1 {{ font-size: 22px; font-weight: 700; color: #f1f5f9; }}
.header h1 em {{ font-style: normal; color: #a78bfa; }}
.header .meta {{ display: flex; gap: 24px; margin-top: 10px; font-size: 13px; color: #94a3b8; flex-wrap: wrap; }}
.header .meta span {{ display: inline-flex; align-items: center; gap: 4px; }}

.container {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}

.section {{ background: #1e293b; border-radius: 12px; padding: 24px; margin-bottom: 24px; border: 1px solid #334155; }}
.section h2 {{ font-size: 17px; font-weight: 600; color: #f1f5f9; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #334155; }}

/* Stats Grid */
.stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; }}
.stat-card {{ background: #0f172a; padding: 14px; border-radius: 8px; text-align: center; }}
.stat-card .stat-value {{ font-size: 26px; font-weight: 700; }}
.stat-card .stat-label {{ font-size: 12px; color: #64748b; margin-top: 4px; }}

/* Year Distribution */
.year-bar {{ display: flex; align-items: flex-end; gap: 4px; padding: 16px 0 0; height: 100px; }}

/* Timeline */
.timeline {{ position: relative; padding: 20px 0; }}
.timeline::before {{ content: ''; position: absolute; left: 24px; top: 0; bottom: 0; width: 2px; background: #334155; }}

.tl-item {{ position: relative; padding: 0 0 20px 56px; }}
.tl-item:last-child {{ padding-bottom: 0; }}

.tl-dot {{ position: absolute; left: 17px; top: 4px; width: 16px; height: 16px; border-radius: 50%; border: 3px solid #0f172a; z-index: 2; }}

.tl-content {{ background: #0f172a; padding: 14px 16px; border-radius: 10px; border: 1px solid #334155; transition: all 0.2s; }}
.tl-content:hover {{ border-color: #6366f1; box-shadow: 0 4px 20px rgba(99,102,241,0.15); }}

.tl-head {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 6px; }}
.tl-seq {{ font-size: 10px; color: #475569; background: #1e293b; padding: 1px 6px; border-radius: 3px; }}
.tl-date {{ font-size: 12px; font-weight: 700; color: #94a3b8; white-space: nowrap; }}
.tl-source {{ font-size: 11px; padding: 1px 8px; border-radius: 3px; background: #1e293b; color: #64748b; }}
.tl-stage {{ font-size: 11px; padding: 2px 10px; border-radius: 4px; font-weight: 500; }}
.tl-title {{ font-size: 13px; color: #e2e8f0; line-height: 1.5; }}
.tl-title-link {{ font-size: 13px; color: #a5b4fc; line-height: 1.5; text-decoration: none; transition: color 0.2s; }}
.tl-title-link:hover {{ color: #818cf8; text-decoration: underline; }}
.tl-link {{ font-size: 11px; color: #64748b; text-decoration: none; margin-left: auto; display: inline-flex; align-items: center; gap: 2px; transition: color 0.2s; }}
.tl-link:hover {{ color: #818cf8; }}
.link-icon {{ font-size: 10px; }}
.tl-content-summary {{ font-size: 12px; color: #64748b; line-height: 1.5; margin-top: 6px; padding-top: 6px; border-top: 1px solid #1e293b; }}
.tl-analysis {{ font-size: 12px; color: #a5b4fc; line-height: 1.6; margin-top: 8px; padding: 8px 10px; border-radius: 6px; background: rgba(99,102,241,0.08); border-left: 2px solid rgba(99,102,241,0.3); }}
.analysis-placeholder {{ color: #475569; font-style: italic; font-size: 12px; }}

/* Filter buttons */
.filter-bar {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }}
.filter-btn {{ padding: 6px 14px; border-radius: 6px; border: 1px solid #334155; background: transparent; color: #94a3b8; font-size: 12px; cursor: pointer; transition: all 0.2s; }}
.filter-btn:hover {{ border-color: #6366f1; color: #e2e8f0; }}
.filter-btn.active {{ background: rgba(99,102,241,0.2); border-color: #6366f1; color: #a5b4fc; }}

/* Summary card */
.summary {{ background: #0f172a; border-radius: 8px; padding: 16px; margin-top: 12px; font-size: 13px; color: #94a3b8; line-height: 1.8; }}
.summary strong {{ color: #e2e8f0; }}

.scroll-top {{ position: fixed; bottom: 30px; right: 30px; width: 44px; height: 44px; border-radius: 50%; background: #6366f1; color: #fff; border: none; font-size: 20px; cursor: pointer; display: none; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(99,102,241,0.3); z-index: 100; }}
.scroll-top:hover {{ background: #4f46e5; }}

.footer {{ text-align: center; padding: 24px; color: #475569; font-size: 12px; border-top: 1px solid #334155; margin-top: 40px; }}

/* Animations */
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.tl-item {{ animation: fadeIn 0.3s ease-out; }}

@media (max-width: 640px) {{
    .header h1 {{ font-size: 18px; }}
    .header .meta {{ gap: 12px; font-size: 12px; }}
    .tl-title {{ font-size: 12px; }}
}}
</style>
</head>
<body>

<div class="header">
    <h1>⏳ CHRONOS 事件追踪 · <em>#{_escape_html(keyword)}</em></h1>
    <div class="meta">
        <span>🏷️ <strong>{stock_name_display}</strong></span>
        <span>📅 回溯: {days} 天</span>
        <span>🕐 {today_str}</span>
        <span>📰 {stats['total']} 条事件</span>
        <span>📋 {stats['ann_count']} 公告 / 📰 {stats['news_count']} 新闻</span>
    </div>
</div>

<div class="container">

<!-- 统计概览 -->
<div class="section">
    <h2>📊 事件概览</h2>
    <div class="stats-grid">
        <div class="stat-card" style="border-top:3px solid #a78bfa;">
            <div class="stat-value" style="color:#a78bfa;">{stats['total']}</div>
            <div class="stat-label">📰 事件总数</div>
        </div>
        <div class="stat-card" style="border-top:3px solid #60a5fa;">
            <div class="stat-value" style="color:#60a5fa;">{stats['ann_count']}</div>
            <div class="stat-label">📋 公告</div>
        </div>
        <div class="stat-card" style="border-top:3px solid #fbbf24;">
            <div class="stat-value" style="color:#fbbf24;">{stats['news_count']}</div>
            <div class="stat-label">📰 新闻</div>
        </div>
{stage_cards}
    </div>
</div>

<!-- 年度分布 -->
<div class="section">
    <h2>📅 年度分布</h2>
    <div class="year-bar">
{year_bar_html}
    </div>
</div>

<!-- 事件时间线 -->
<div class="section">
    <h2>📰 <em>{_escape_html(keyword)}</em> 事件时间线</h2>
    <div class="filter-bar" id="filterBar">
        <button class="filter-btn active" data-stage="all" onclick="filterTimeline('all')">全部</button>
        <button class="filter-btn" data-stage="预备期" onclick="filterTimeline('预备期')" style="border-color:#60a5fa40;color:#60a5fa;">📋 预备期</button>
        <button class="filter-btn" data-stage="实施期" onclick="filterTimeline('实施期')" style="border-color:#fbbf2440;color:#fbbf24;">🔧 实施期</button>
        <button class="filter-btn" data-stage="完成期" onclick="filterTimeline('完成期')" style="border-color:#34d39940;color:#34d399;">✅ 完成期</button>
        <button class="filter-btn" data-stage="其他" onclick="filterTimeline('其他')" style="border-color:#94a3b840;color:#94a3b8;">📌 其他</button>
    </div>
    <div class="timeline" id="timeline">
"""

    for e in timeline:
        stage = e.get("stage", "其他")
        colors = stage_colors.get(stage, stage_colors["其他"])
        icon = stage_icons.get(stage, "📌")
        title = _escape_html(e["title"])
        event_url = e.get("url", "")
        event_content = e.get("content", "")

        # 标题（可点击）
        if event_url:
            title_html = f'<a href="{event_url}" target="_blank" class="tl-title-link" title="查看原文">{title}</a>'
            link_html = f'<a href="{event_url}" target="_blank" class="tl-link" title="查看原文"><span class="link-icon">🔗</span> 原文</a>'
        else:
            title_html = f'<span class="tl-title">{title}</span>'
            link_html = ""

        # 内容摘要（仅新闻有）
        content_html = ""
        if event_content:
            # 去掉 HTML 标签
            clean_content = event_content.replace("<em>", "").replace("</em>", "").replace("<p>", "").replace("</p>", "")
            if len(clean_content) > 200:
                clean_content = clean_content[:200] + "…"
            content_html = f'<div class="tl-content-summary">{_escape_html(clean_content)}</div>'

        # AI 评估占位
        # 若外部传入了 analysis_map，使用对应内容；否则显示占位符
        placeholder = "[AI评估待补充] 点击原文链接阅读后，在此填入你的分析"
        if analysis_map and e["seq"] in analysis_map and analysis_map[e["seq"]]:
            analysis_content = _escape_html(analysis_map[e["seq"]])
        else:
            analysis_content = placeholder
        analysis_html = (
            f'<div class="tl-analysis" data-seq="{e["seq"]}">'
            f'<div class="analysis-placeholder">'
            f'{analysis_content}'
            f'</div></div>'
        )

        html += f"""        <div class="tl-item" data-stage="{stage}">
            <div class="tl-dot" style="background:{colors['dot']};"></div>
            <div class="tl-content">
                <div class="tl-head">
                    <span class="tl-seq">#{e['seq']}</span>
                    <span class="tl-date">{e['date']}</span>
                    <span class="tl-source">{e['source']}</span>
                    <span class="tl-stage" style="background:{colors['bg']};color:{colors['text']};">{icon} {stage}</span>
                    {link_html}
                </div>
                <div class="tl-title">{title_html}</div>
                {content_html}
                {analysis_html}
            </div>
        </div>
"""

    html += """    </div>
</div>

<!-- 事件摘要 -->
<div class="section">
    <h2>📝 事件摘要</h2>
    <div class="summary">
"""

    # 摘要内容
    first_date = timeline[0]["date"] if timeline else ""
    last_date = timeline[-1]["date"] if timeline else ""
    stage_summary = " → ".join(
        f"{s}({c})" for s in ["预备期", "实施期", "完成期"]
        if (c := stats["stage_counts"].get(s, 0)) > 0
    )

    html += f"""        <p><strong>追踪关键词</strong>：#{_escape_html(keyword)}</p>
        <p><strong>时间跨度</strong>：{stats['time_span']}</p>
        <p><strong>事件总量</strong>：{stats['total']} 条（公告 {stats['ann_count']} 条 / 新闻 {stats['news_count']} 条）</p>
        <p><strong>阶段分布</strong>：{stage_summary}</p>
        <p><strong>最早事件</strong>：{first_date} — {_escape_html(timeline[0]['title'])}</p>
        <p><strong>最近事件</strong>：{last_date} — {_escape_html(timeline[-1]['title'])}</p>
"""

    # 年度摘要
    if stats["year_counts"]:
        year_lines = " · ".join(
            f"{y}: {c}条" for y, c in sorted(stats["year_counts"].items())
        )
        html += f"""        <p><strong>年度分布</strong>：{year_lines}</p>
"""

    html += """    </div>
</div>

</div>

<button class="scroll-top" id="scrollTopBtn" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>

<div class="footer">
    <p>📊 数据来源: 巨潮资讯网（公告）· 东方财富（新闻）</p>
    <p>⚙️ CHRONOS 事件追踪 · 纯规则驱动，不含 LLM 分析</p>
    <p>⚠️ 本分析仅供参考，不构成投资建议。</p>
</div>

<script>
// 阶段过滤
function filterTimeline(stage) {
    const items = document.querySelectorAll('.tl-item');
    const btns = document.querySelectorAll('.filter-btn');
    btns.forEach(b => b.classList.remove('active'));
    const activeBtn = document.querySelector(`.filter-btn[data-stage="${stage}"]`);
    if (activeBtn) activeBtn.classList.add('active');
    items.forEach(item => {
        if (stage === 'all' || item.dataset.stage === stage) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// 滚动返回顶部
window.addEventListener('scroll', function() {
    const btn = document.getElementById('scrollTopBtn');
    btn.style.display = window.scrollY > 400 ? 'flex' : 'none';
});
</script>

</body>
</html>"""
    return html


# ============================================================
# 主流程
# ============================================================

def main():
    sys.stdout.reconfigure(encoding="utf-8")

    # ---- 解析标志参数 ----
    args_list = sys.argv[1:]
    relaxed = False
    export_candidates_path = None
    build_report_path = None

    # 提取 --export-candidates 的值
    if "--export-candidates" in args_list:
        idx = args_list.index("--export-candidates")
        if idx + 1 < len(args_list) and not args_list[idx + 1].startswith("--"):
            export_candidates_path = args_list[idx + 1]

    # 提取 --build-report 的值
    if "--build-report" in args_list:
        idx = args_list.index("--build-report")
        if idx + 1 < len(args_list) and not args_list[idx + 1].startswith("--"):
            build_report_path = args_list[idx + 1]

    relaxed = "--relax" in args_list

    # ---- --build-report 模式：从 AI 标注 JSON 重建 HTML ----
    if build_report_path:
        build_report_from_annotated(build_report_path)
        return

    # ---- 提取位置参数（股票代码、关键词、天数） ----
    # 过滤掉 --flags 及其值
    skip_next = False
    positional = []
    for a in args_list:
        if skip_next:
            skip_next = False
            continue
        if a == "--export-candidates" or a == "--build-report":
            skip_next = True
            continue
        if a == "--relax":
            continue
        positional.append(a)

    if len(positional) < 2:
        print("=" * 50)
        print("  CHRONOS 事件追踪分析 (chronos-timeline)")
        print("=" * 50)
        print()
        print("  用法: python main.py <股票代码> <事件关键词> [天数] [选项]")
        print()
        print("  选项:")
        print("    --relax                  宽松模式（字符级匹配，最大化召回）")
        print("    --export-candidates FILE  导出候选事件为 JSON（供 AI 标注）")
        print("    --build-report FILE       从 AI 标注的 JSON 生成 HTML 报告")
        print()
        print("  示例:")
        print("    python main.py 600519 回购")
        print("    python main.py 600338 锂矿 --relax --export-candidates cand.json")
        print("    python main.py --build-report annotated.json")
        print("    python main.py 600519 利润分配")
        print("    python main.py 000651 增持 365")
        print()
        sys.exit(1)

    stock_code = positional[0]
    keyword = positional[1]
    stock_name = get_stock_name(stock_code)
    days = DEFAULT_DAYS
    for a in positional[2:]:
        if a.isdigit():
            days = int(a)
            break

    # Step 1: 获取公告
    print(f"📋 获取公告 {stock_name}...", end=" ")
    sys.stdout.flush()
    cninfo_items = get_cninfo_data(stock_code, days)
    print(f"{len(cninfo_items)} 条")

    # Step 2: 获取新闻
    print(f"📰 获取新闻...", end=" ")
    sys.stdout.flush()
    try:
        news_items = get_news_data(stock_code, days, stock_name)
        print(f"{len(news_items)} 条")
    except Exception as e:
        news_items = []
        print(f"跳过（{e}）")

    # Step 3: 关键词过滤（宽松 / 严格）
    all_events = cninfo_items + news_items
    if relaxed:
        filtered = filter_by_keyword_relaxed(all_events, keyword)
        print(f"🔍 宽松匹配「{keyword}」: {len(filtered)}/{len(all_events)} 条")
    else:
        filtered = filter_by_keyword(all_events, keyword)
        print(f"🔍 匹配「{keyword}」: {len(filtered)}/{len(all_events)} 条")

    if not filtered:
        print(f"❌ 未找到与「{keyword}」相关的事件。")
        if relaxed:
            print("💡 提示: 宽松模式仍无结果，可尝试更换关键词。")
        else:
            print("💡 提示: 尝试 --relax 模式以获得更多候选事件。")
        sys.exit(0)

    # Step 4: 构建时间线
    timeline = build_timeline(filtered)

    # ---- --export-candidates 模式：导出 JSON 并退出 ----
    if export_candidates_path:
        export_candidates_json(timeline, export_candidates_path,
                               stock_code, stock_name, keyword, days)
        return

    # Step 5: 统计
    stats = compute_stats(timeline, keyword)

    # Step 6: 生成 HTML
    print(f"📄 生成 HTML 报告...", end=" ")
    sys.stdout.flush()
    html = format_html_report(stock_code, stock_name, keyword, days, timeline, stats)

    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    safe_keyword = keyword.replace("/", "_").replace("\\", "_").replace(" ", "_")
    filepath = os.path.join(output_dir, f"{stock_code}_{safe_keyword}_chronos.html")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK")
    print(f"   → {filepath}")
    print(f"声明: 本分析仅供参考，不构成投资建议。")


if __name__ == "__main__":
    main()
