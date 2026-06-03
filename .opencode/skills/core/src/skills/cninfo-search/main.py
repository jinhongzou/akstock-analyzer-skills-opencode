# -*- coding: utf-8 -*-
"""
Cninfo Search - 巨潮资讯网公告搜索工具
用法: python main.py <股票代码或名称> [选项]

示例:
  python main.py 600519
  python main.py 贵州茅台 --from 2026-01-01 --to 2026-06-01 --pdf
  python main.py 西藏珠峰 --page 2 --size 30
  python main.py 金戈新材 --plate bj
"""

import sys
import os
import re
import json
from datetime import datetime
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("错误: 请先安装 requests 库: pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

API_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
PDF_BASE = "http://static.cninfo.com.cn/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "http://www.cninfo.com.cn/new/index",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


# ---------------------------------------------------------------------------
# 核心查询函数
# ---------------------------------------------------------------------------

def query_announcements(
    searchkey: str = "",
    stock: str = "",
    page: int = 1,
    size: int = 20,
    date_from: str = "",
    date_to: str = "",
    plate: str = "",
    category: str = "",
) -> dict:
    """
    查询巨潮资讯网公告

    参数:
        searchkey: 搜索关键词（公司名称）
        stock: 股票代码
        page: 页码
        size: 每页条数
        date_from: 起始日期 YYYY-MM-DD
        date_to: 截止日期 YYYY-MM-DD
        plate: 板块 sh/sz/bj
        category: 公告类别编码

    返回:
        API 响应的 JSON 字典
    """
    data = {
        "pageNum": str(page),
        "pageSize": str(min(size, 50)),
        "isHLtitle": "true",
        "seDate": "",
        "sord": "date",
        "order": "desc",
    }

    if searchkey:
        data["searchkey"] = searchkey
    if stock:
        data["stock"] = f"{stock},{stock}"
    if plate:
        data["plate"] = plate
        plate_names = {"sh": "沪市", "sz": "深市", "bj": "北交所"}
        data["tabKey"] = plate_names.get(plate, plate)
    if category:
        data["category"] = category
    if date_from and date_to:
        data["seDate"] = f"{date_from}~{date_to}"
    elif date_from:
        data["seDate"] = f"{date_from}~"
    elif date_to:
        data["seDate"] = f"~{date_to}"

    try:
        resp = requests.post(API_URL, data=data, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        result = resp.json()
        return result
    except requests.exceptions.Timeout:
        return {"error": "请求超时，请稍后重试"}
    except requests.exceptions.ConnectionError:
        return {"error": "网络连接失败，请检查网络"}
    except json.JSONDecodeError:
        return {"error": f"API 返回非 JSON 数据: {resp.text[:200]}"}
    except Exception as e:
        return {"error": f"请求失败: {str(e)}"}


def parse_timestamp(ts_ms: int) -> str:
    """将毫秒时间戳转为日期字符串"""
    if not ts_ms:
        return ""
    try:
        return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")
    except:
        return str(ts_ms)


def is_stock_code(text: str) -> bool:
    """判断是否为股票代码（纯数字 6位或8位）"""
    return bool(re.match(r"^\d{4,8}$", text.strip()))


# ---------------------------------------------------------------------------
# 输出格式化
# ---------------------------------------------------------------------------

def format_results(result: dict, show_pdf: bool = False, full_mode: bool = False) -> str:
    """格式化查询结果为可读字符串"""
    if "error" in result:
        return f"错误: {result['error']}"

    announcements = result.get("announcements")
    if announcements is None:
        return "未找到公告数据"

    total = result.get("totalAnnouncement", 0)
    page_size = len(announcements)

    lines = []
    lines.append("=" * 72)
    lines.append(f"  巨潮资讯网公告查询结果")
    lines.append(f"  共 {total} 条公告 | 当前显示 {page_size} 条")
    lines.append("=" * 72)
    lines.append("")

    for i, ann in enumerate(announcements, 1):
        code = ann.get("secCode", "")
        name = ann.get("secName", "")
        title = ann.get("announcementTitle", "")
        date_str = parse_timestamp(ann.get("announcementTime"))
        adj_url = ann.get("adjunctUrl", "")

        lines.append(f"[{i}] {title}")
        lines.append(f"    代码: {code} | {name} | 日期: {date_str}")

        if show_pdf and adj_url:
            lines.append(f"    PDF: {PDF_BASE}{adj_url}")
        elif adj_url:
            lines.append(f"    PDF: {adj_url}")

        if full_mode:
            atype = ann.get("announcementType", "")
            org_id = ann.get("orgId", "")
            ann_id = ann.get("announcementId", "")
            col_id = ann.get("columnId", "")
            page_col = ann.get("pageColumn", "")
            lines.append(f"    类别编码: {atype}")
            lines.append(f"    orgId: {org_id} | 公告ID: {ann_id}")
            lines.append(f"    columnId: {col_id} | pageColumn: {page_col}")

        lines.append("")

    # 分页提示
    page_num = 1
    # 从原始 data 中无法直接获知页码，从 result 结构推断
    if total > page_size:
        has_more = result.get("hasMore", False)
        if has_more:
            lines.append(f"--- 还有更多公告，使用 --page N 翻页 ---")
        lines.append(f"")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 参数解析
# ---------------------------------------------------------------------------

def parse_args(argv: list) -> dict:
    """解析命令行参数"""
    args = {
        "query": "",
        "page": 1,
        "size": 20,
        "date_from": "",
        "date_to": "",
        "plate": "",
        "category": "",
        "show_pdf": False,
        "full_mode": False,
    }

    i = 1
    while i < len(argv):
        arg = argv[i]

        if arg == "--page" and i + 1 < len(argv):
            args["page"] = int(argv[i + 1])
            i += 2
        elif arg == "--size" and i + 1 < len(argv):
            args["size"] = int(argv[i + 1])
            i += 2
        elif arg == "--from" and i + 1 < len(argv):
            args["date_from"] = argv[i + 1]
            i += 2
        elif arg == "--to" and i + 1 < len(argv):
            args["date_to"] = argv[i + 1]
            i += 2
        elif arg == "--plate" and i + 1 < len(argv):
            args["plate"] = argv[i + 1]
            i += 2
        elif arg == "--category" and i + 1 < len(argv):
            args["category"] = argv[i + 1]
            i += 2
        elif arg == "--pdf":
            args["show_pdf"] = True
            i += 1
        elif arg == "--full":
            args["full_mode"] = True
            i += 1
        elif arg.startswith("--"):
            print(f"未知选项: {arg}")
            sys.exit(1)
        else:
            args["query"] = arg
            i += 1

    return args


def print_usage():
    """打印使用说明"""
    print("=" * 60)
    print("  巨潮资讯网公告搜索工具 (cninfo-search)")
    print("=" * 60)
    print("")
    print("用法:")
    print("  python main.py <股票代码或公司名称> [选项]")
    print("")
    print("选项:")
    print("  --from <日期>    起始日期 (YYYY-MM-DD)")
    print("  --to <日期>      截止日期 (YYYY-MM-DD)")
    print("  --page <页码>    页码 (默认 1)")
    print("  --size <条数>    每页条数 (默认 20, 最大 50)")
    print("  --plate <板块>   板块: sh(沪市)/sz(深市)/bj(北交所)")
    print("  --category <编码> 公告类别编码")
    print("  --pdf            显示完整 PDF 下载链接")
    print("  --full           显示全部字段")
    print("")
    print("示例:")
    print('  python main.py 600519')
    print('  python main.py 贵州茅台 --from 2026-01-01 --pdf')
    print('  python main.py 西藏珠峰 --page 2 --size 30')
    print('  python main.py 金戈新材 --plate bj --full')
    print("")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args(sys.argv)

    if not args["query"]:
        print_usage()
        sys.exit(0)

    query = args["query"].strip()

    # 判断输入是股票代码还是公司名称
    if is_stock_code(query):
        # 先尝试用 stock 参数精确查询
        result = query_announcements(
            stock=query,
            page=args["page"],
            size=args["size"],
            date_from=args["date_from"],
            date_to=args["date_to"],
            plate=args["plate"],
            category=args["category"],
        )
        anns = result.get("announcements")
        total = result.get("totalAnnouncement", 0)

        # 如果 stock 查询没结果，转名称搜索
        if not anns or total == 0:
            result = query_announcements(
                searchkey=query,
                page=args["page"],
                size=args["size"],
                date_from=args["date_from"],
                date_to=args["date_to"],
                plate=args["plate"],
                category=args["category"],
            )
    else:
        # 公司名称，直接 searchkey 搜索
        result = query_announcements(
            searchkey=query,
            page=args["page"],
            size=args["size"],
            date_from=args["date_from"],
            date_to=args["date_to"],
            plate=args["plate"],
            category=args["category"],
        )

    print(format_results(result, show_pdf=args["show_pdf"], full_mode=args["full_mode"]))

    # 处理错误
    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
