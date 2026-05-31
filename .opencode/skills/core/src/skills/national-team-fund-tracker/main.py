# -*- coding: utf-8 -*-
"""
国家队ETF持仓规模追踪 - 数据采集入口

数据源: Tushare fund_share（日频份额数据）
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import NationalTeamFundTracker


def _default_date_range(years=10):
    """返回默认起止日期 YYYYMMDD，往前推 years 年"""
    today = datetime.today()
    start = today - timedelta(days=years * 365.25)
    return start.strftime("%Y%m%d"), today.strftime("%Y%m%d")


def main():
    tracker = NationalTeamFundTracker()

    # 日期范围: 可传参，默认近10年
    start_date = sys.argv[1] if len(sys.argv) > 1 else None
    end_date = sys.argv[2] if len(sys.argv) > 2 else None
    if not start_date or not end_date:
        start_date, end_date = _default_date_range(10)

    print("=" * 90)
    print("  国家队ETF持仓规模追踪")
    print(f"  数据源: Tushare fund_share（日频份额，取月末值）")
    print(f"  追踪标的: 汇金系重仓的8只核心宽基ETF")
    print(f"  数据区间: {start_date[:4]}-{start_date[4:6]} ~ {end_date[:4]}-{end_date[4:6]}")
    print("=" * 90)

    # Step 1: 获取月度汇总数据
    data = tracker.get_monthly_summary(start_date, end_date)
    if not data["series"]:
        print("\n无数据")
        return

    series = data["series"]
    details = data["etf_details"]
    summary = data["summary"]

    # Step 2: 输出月度总量趋势
    print(f"\n{'─' * 90}")
    print("  一、月度总量趋势")
    print(f"{'─' * 90}")

    # 表头
    header = f"{'月份':<10}"
    for code in ["510300.SH", "510050.SH", "510310.SH", "510330.SH",
                  "159919.SZ", "159845.SZ", "512100.SH", "588000.SH"]:
        if code in details:
            header += f"  {details[code]['name'][:10]:>12}"
    header += f"  {'合计(万份)':>14}  {'环比':>10}"
    print(header)
    print(f"{'─' * len(header)}")

    for entry in series:
        line = f"{entry['month']:<10}"
        for code in ["510300.SH", "510050.SH", "510310.SH", "510330.SH",
                      "159919.SZ", "159845.SZ", "512100.SH", "588000.SH"]:
            if code in details:
                found = [v for v in details[code]["values"] if v["month"] == entry["month"]]
                if found:
                    line += f"  {found[0]['fd_share']:>12,.0f}"
                else:
                    line += f"  {'---':>12}"
            else:
                line += f"  {'N/A':>12}"

        if entry["month"] == series[0]["month"]:
            line += f"  {entry['total']:>14,.0f}  {'(基期)':>10}"
        else:
            change_str = f"{entry.get('change_pct', 0):+.2f}%"
            line += f"  {entry['total']:>14,.0f}  {change_str:>10}"
        print(line)

    print()
    print(f"  统计区间: {summary['first_month']} ~ {summary['last_month']}")
    print(f"  总规模变化: {summary['first_total']:>12,.0f} -> {summary['last_total']:>12,.0f} 万份")
    print(f"  累计变化: {summary['total_change']:>+12,.0f} 万份 ({summary['total_change_pct']:+.2f}%)")

    # Step 3: 结构分析
    print(f"\n{'─' * 90}")
    print("  二、结构分析")
    print(f"{'─' * 90}")

    # 按类型分组
    last_month = series[-1]["month"]
    hs300_total = 0
    sz50_total = 0
    kcb50_total = 0
    zz1000_total = 0

    for code in ["510300.SH", "510310.SH", "510330.SH", "159919.SZ"]:
        if code in details:
            found = [v for v in details[code]["values"] if v["month"] == last_month]
            if found:
                hs300_total += found[0]["fd_share"]
    if "510050.SH" in details:
        found = [v for v in details["510050.SH"]["values"] if v["month"] == last_month]
        if found:
            sz50_total = found[0]["fd_share"]
    if "588000.SH" in details:
        found = [v for v in details["588000.SH"]["values"] if v["month"] == last_month]
        if found:
            kcb50_total = found[0]["fd_share"]
    for code in ["159845.SZ", "512100.SH"]:
        if code in details:
            found = [v for v in details[code]["values"] if v["month"] == last_month]
            if found:
                zz1000_total += found[0]["fd_share"]

    total = hs300_total + sz50_total + kcb50_total + zz1000_total
    if total > 0:
        print(f"  沪深300类合计: {hs300_total:>12,.0f} 万份 (占比 {hs300_total/total*100:5.1f}%)")
        print(f"  上证50ETF:     {sz50_total:>12,.0f} 万份 (占比 {sz50_total/total*100:5.1f}%)")
        print(f"  科创50ETF:     {kcb50_total:>12,.0f} 万份 (占比 {kcb50_total/total*100:5.1f}%)")
        print(f"  中证1000类合计:{zz1000_total:>12,.0f} 万份 (占比 {zz1000_total/total*100:5.1f}%)")

    # Step 4: NAV验证（对最近的大幅变化月份）
    print(f"\n{'─' * 90}")
    print("  三、NAV交叉验证（近期大幅变化月份）")
    print(f"{'─' * 90}")

    # 找到最近3个月中变化 >5% 的月份
    significant_changes = []
    for entry in series[-6:]:
        if entry["month"] != series[0]["month"] and abs(entry.get("change_pct", 0)) > 5:
            significant_changes.append(entry["month"])

    if significant_changes:
        for code in ["510300.SH", "588000.SH"]:
            if code not in details:
                continue
            cname = details[code]["name"]
            print(f"\n  {code} {cname}:")
            for sm in significant_changes[:2]:
                try:
                    year, m = sm.split("-")
                    bf = f"{year}{m}01"
                    af = f"{year}{m}28"
                    result = tracker.verify_drop_is_real(code, bf, af)
                    if "error" not in result:
                        print(f"    {sm}: 份额{result['share_change_pct']:+.1f}% | "
                              f"NAV{result['nav_change_pct']:+.1f}%")
                except Exception:
                    pass
    else:
        print("  近6个月无超过5%的大幅变化")

    print(f"\n{'=' * 90}")
    print("  分析数据采集完成，请基于以上数据结合SKILL.md框架进行分析判断")
    print("  注意: fd_share为ETF总份额(万份)，非汇金单独持仓")
    print("=" * 90)


if __name__ == "__main__":
    main()
