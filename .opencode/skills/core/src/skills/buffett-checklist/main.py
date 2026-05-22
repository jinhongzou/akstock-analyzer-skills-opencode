# -*- coding: utf-8 -*-
"""
巴菲特6关检查清单 — 数据聚合器

只聚合原始数据，不包含AI评估结论。
AI根据本脚本输出的结构化数据 + 自身商业认知，独立完成六关评估。

调用方式:
    python main.py <股票代码>

聚合的数据源:
    - StockAnalyzer:      行情估值 / 价格分布
    - FinancialAnalyzer:  ROCE历史 / 财务健康指标
    - ShareholderAnalyzer:股东结构 / 质押 / 回购
    - DividendAnalyzer:   分红配送 / 分红连续性
    - TechnicalAnalyzer:  均线 / RSI
"""
import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import (
    get_stock_profile,
    calculate_roce_history,
    analyze_financial_health,
    get_top_circulating_holders,
    get_pledge_data,
    get_repurchase_data,
    get_a_dividend_detail,
    analyze_dividend_consistency,
    calculate_price_distribution,
    get_historical_data,
    calculate_ma,
    calculate_rsi,
)
from datetime import datetime, timedelta


def fmt(val, suffix=""):
    """安全格式化数值"""
    if val is None:
        return "N/A"
    try:
        float(val)
        return f"{val}{suffix}"
    except (ValueError, TypeError):
        return str(val)


def section(title):
    """输出章节标题"""
    print(f"\n{'=' * 60}")
    print(f"  【{title}】")
    print(f"{'=' * 60}")


def kv(key, val):
    """输出键值对"""
    print(f"  {key}: {val}")


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码>")
        sys.exit(1)

    stock_code = sys.argv[1]
    print(f"\n>>> 巴菲特检查清单数据聚合: {stock_code}")
    print(f">>> 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f">>> 注意: 以下为原始数据, AI 需独立完成评估")

    # ════════════════════════════════════════════
    # 1. 基本行情
    # ════════════════════════════════════════════
    section("基本行情")
    profile = get_stock_profile(stock_code)
    if profile:
        kv("股票名称", profile.get("名称", "N/A"))
        kv("行业", profile.get("行业", "N/A"))
        kv("现价", fmt(profile.get("现价"), " 元"))
        kv("涨跌幅", fmt(profile.get("涨幅"), "%"))
        kv("市盈率(动)", fmt(profile.get("市盈率(动)")))
        kv("市盈率(TTM)", fmt(profile.get("市盈率(TTM)")))
        kv("市净率", fmt(profile.get("市净率")))
        kv("股息率(TTM)", fmt(profile.get("股息率(TTM)"), "%"))
        kv("总市值", fmt(profile.get("资产净值/总市值"), " 亿"))
        kv("每股收益", fmt(profile.get("每股收益"), " 元"))
        kv("每股净资产", fmt(profile.get("每股净资产"), " 元"))
    else:
        print("  [X] 获取基本行情失败")

    # ════════════════════════════════════════════
    # 2. ROCE 历史
    # ════════════════════════════════════════════
    section("ROCE 历史")
    roce_data = calculate_roce_history(stock_code)
    if roce_data:
        print(f"  {'年份':<6} {'ROCE':<8} {'净利润(亿)':<12} {'EBIT(亿)':<12} {'投入资本(亿)':<14} {'公式':<6}")
        print(f"  {'-'*58}")
        for r in roce_data:
            formula = "修正" if r.get("formula_used") == "modified" else "原始"
            net = r["net_profit"] / 1e8 if r["net_profit"] else 0
            ebit = r["ebit"] / 1e8 if r["ebit"] else 0
            cap = r["capital"] / 1e8 if r["capital"] else 0
            print(f"  {r['year']:<6} {r['roce']:<8.2%} {net:<12.1f} {ebit:<12.1f} {cap:<14.1f} {formula:<6}")

        # 汇总统计（只算数值不判断）
        recent_5 = [r["roce"] for r in roce_data[:5]]
        recent_3 = [r["roce"] for r in roce_data[:3]]
        all_roce = [r["roce"] for r in roce_data]
        kv("近3年ROCE均值", f"{sum(recent_3)/len(recent_3):.2%}" if recent_3 else "N/A")
        kv("近5年ROCE均值", f"{sum(recent_5)/len(recent_5):.2%}" if recent_5 else "N/A")
        kv("全部年份ROCE均值", f"{sum(all_roce)/len(all_roce):.2%}" if all_roce else "N/A")
        kv("ROCE记录年数", f"{len(roce_data)} 年")

        # 趋势方向（只展示升降，不判断好坏）
        if len(roce_data) >= 3:
            first_3_avg = sum(r["roce"] for r in roce_data[-3:]) / 3
            last_3_avg = sum(r["roce"] for r in roce_data[:3]) / 3
            direction = "上升" if last_3_avg > first_3_avg * 1.1 else ("下降" if last_3_avg < first_3_avg * 0.9 else "平稳")
            kv("近3年vs最早3年均值对比", f"最早3年均值={first_3_avg:.2%}, 近3年均值={last_3_avg:.2%}, 趋势方向={direction}")

        # 净现金（只展示数值）
        latest = roce_data[0]
        cash = latest.get("cash", 0)
        interest_debt = latest.get("interest_debt", 0)
        equity = latest.get("equity_total", 0)
        net_cash = cash - interest_debt
        kv("最新货币资金", f"{cash/1e8:.1f} 亿")
        kv("最新有息负债", f"{interest_debt/1e8:.1f} 亿")
        kv("最新股东权益", f"{equity/1e8:.1f} 亿")
        kv("净现金(货币资金-有息负债)", f"{net_cash/1e8:+.1f} 亿")
    else:
        print("  [X] 获取ROCE数据失败")

    # ════════════════════════════════════════════
    # 3. 财务健康
    # ════════════════════════════════════════════
    section("财务健康")
    health = analyze_financial_health(stock_code)
    if health.get("ratios"):
        print(f"  {'日期':<12} {'流动比率':<10} {'速动比率':<10} {'资产负债率':<12} {'ROE':<10}")
        print(f"  {'-'*54}")
        for r in health["ratios"]:
            print(f"  {str(r['date'])[:10]:<12} {r['current_ratio']:<10.2f} {r['quick_ratio']:<10.2f} {r['debt_ratio']:<12.2%} {r['roe']:<10.2%}")

        # 最新一期指标
        latest_h = health["ratios"][0]
        kv("最新资产负债率", f"{latest_h['debt_ratio']:.2%}")
        kv("最新流动比率", f"{latest_h['current_ratio']:.2f}")
        kv("最新ROE", f"{latest_h['roe']:.2%}")

    if health.get("cash_flow"):
        print(f"\n  --- 现金流 ---")
        for c in health["cash_flow"][:3]:
            kv(f"  {str(c['date'])[:10]} 经营现金流", f"{c['ocf']/1e8:.1f} 亿")
            kv(f"  {str(c['date'])[:10]} 自由现金流", f"{c['fcf']/1e8:.1f} 亿")

        # OCF vs 净利润对比（仅展示数据，不判断）
        # 注意：现金流数据可能为季度值，ROCE净利润为年报值，AI需自行判断时期间隔
        if health.get("cash_flow") and roce_data:
            for cf in health["cash_flow"][:2]:
                cf_date = str(cf.get("date", ""))[:10]
                # 尝试匹配对应年份的ROCE净利润
                cf_year = cf_date[:4] if len(cf_date) >= 4 else ""
                match_profit = next((r["net_profit"] for r in roce_data if str(r["year"]) == cf_year), None)
                if match_profit and match_profit > 0:
                    ratio = cf["ocf"] / match_profit if match_profit else 0
                    kv(f"  {cf_date} OCF / {cf_year}年净利润", f"{ratio:.2f}x")
    else:
        print("  [X] 获取财务健康数据失败")

    # ════════════════════════════════════════════
    # 4. 股东结构
    # ════════════════════════════════════════════
    section("股东结构")
    holders = get_top_circulating_holders(stock_code)
    if holders.get("holders"):
        holders_list = holders["holders"]
        total_pct = sum(h.get("占流通股比例", 0) for h in holders_list[:10])
        kv("十大股东合计持股", f"{total_pct:.1f}%")

        print(f"\n  --- 前5大股东 ---")
        for i, h in enumerate(holders_list[:5], 1):
            name = h.get("股东名称", "N/A")
            shares = h.get("持股数量", 0)
            pct = h.get("占流通股比例", 0)
            kv(f"  #{i} {name[:30]}", f"{shares/1e4:.1f}万股 ({pct:.2f}%)")
    else:
        print("  [X] 获取股东数据失败")

    # 股权质押
    pledge = get_pledge_data(stock_code)
    if pledge and pledge.get("summary"):
        summary = pledge["summary"]
        kv("总质押比例", summary.get("总质押比例", "无"))
        kv("质押总市值", summary.get("质押总市值(亿元)", "N/A"))
        kv("质押笔数", summary.get("质押笔数", "N/A"))
    else:
        kv("股权质押", "无质押数据")

    # 股份回购
    repurchase = get_repurchase_data(stock_code)
    if repurchase and repurchase.get("summary"):
        s = repurchase["summary"]
        kv("回购次数", s.get("回购次数", 0))
        kv("是否正在回购", s.get("是否正在进行回购", "否"))
        kv("累计回购金额", f"{s.get('回购金额(亿元)', 'N/A')} 亿" if s.get("回购金额(亿元)") else "N/A")
    else:
        kv("股份回购", "无回购数据")

    # ════════════════════════════════════════════
    # 5. 分红数据
    # ════════════════════════════════════════════
    section("分红数据")
    dividend_df = get_a_dividend_detail(stock_code)
    if not dividend_df.empty:
        kv("总分红记录数", len(dividend_df))

        consistency = analyze_dividend_consistency(df=dividend_df)
        if "error" not in consistency:
            kv("现金分红年份数", consistency.get("years_with_cash_dividend", "N/A"))
            kv("送股年份数", consistency.get("years_with_stock_dividend", "N/A"))
            kv("转股年份数", consistency.get("years_with_transfer", "N/A"))
            kv("平均股息率", fmt(consistency.get("avg_dividend_yield", "N/A"), "%"))
            kv("分红连续性评价", consistency.get("consistency", "N/A"))

        # 前5条分红记录
        print(f"\n  --- 最近5条分红记录 ---")
        # 按报告期倒序排列
        if "报告期" in dividend_df.columns:
            sorted_df = dividend_df.sort_values("报告期", ascending=False)
        else:
            sorted_df = dividend_df
        cols = ["报告期", "现金分红-现金分红比例", "现金分红-股息率", "送转股份-送转总比例"]
        available = [c for c in cols if c in sorted_df.columns]
        if available:
            print(f"  {'报告期':<12} {'每股分红(元)':<14} {'股息率':<8}")
            print(f"  {'-'*34}")
            for _, row in sorted_df.head(5).iterrows():
                period = str(row.get("报告期", ""))[:10]
                cash = row.get("现金分红-现金分红比例", "N/A")
                if cash != "N/A" and pd.notna(cash):
                    cash_per_share = cash / 10.0
                    yield_val = row.get("现金分红-股息率", "N/A")
                    yield_str = f"{yield_val:.4f}" if yield_val != "N/A" and pd.notna(yield_val) else "N/A"
                    print(f"  {period:<12} {cash_per_share:<14.2f} {yield_str:<8}")
    else:
        print("  [X] 获取分红数据失败")

    # ════════════════════════════════════════════
    # 6. 价格分布
    # ════════════════════════════════════════════
    section("52周价格分布")
    price_dist = calculate_price_distribution(stock_code)
    if price_dist:
        kv("52周最高价", f"{price_dist['high_52w']:.2f} 元")
        kv("52周最低价", f"{price_dist['low_52w']:.2f} 元")
        kv("中位数", f"{price_dist['median']:.2f} 元")
        kv("Q1(25%分位)", f"{price_dist['q1']:.2f} 元")
        kv("Q3(75%分位)", f"{price_dist['q3']:.2f} 元")
        kv("当前位置分位", f"{price_dist['position_pct']:.1f}%")
    else:
        print("  [X] 获取价格分布数据失败")

    # ════════════════════════════════════════════
    # 7. 技术面
    # ════════════════════════════════════════════
    section("技术面")
    try:
        start = (datetime.now() - timedelta(days=400)).strftime("%Y%m%d")
        df = get_historical_data(stock_code, start_date=start)
        if df is not None and not df.empty:
            kv("数据交易日数", len(df))

            ma = calculate_ma(df)
            if ma:
                kv("MA50", f"{ma.get('ma50', 0):.2f} 元")
                kv("MA200", f"{ma.get('ma200', 0):.2f} 元")
                kv("均线信号", ma.get("signal", "N/A"))
                if ma.get("note"):
                    kv("均线备注", ma.get("note", ""))

            rsi = calculate_rsi(df)
            if rsi:
                kv("RSI(14)", f"{rsi.get('rsi', 0):.2f}")
                kv("RSI信号", rsi.get("signal", "N/A"))
        else:
            print("  [X] 获取历史数据失败")
    except Exception as e:
        print(f"  [X] 技术面数据获取异常: {e}")

    # ════════════════════════════════════════════
    # 结束
    # ════════════════════════════════════════════
    print(f"\n{'=' * 60}")
    print(f">>> 原始数据聚合完毕。AI请基于以上数据 + 自身商业认知")
    print(f">>> 运行6关检查清单，输出完整评估报告。")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
