# -*- coding: utf-8 -*-
"""
A股分红配送详情 - 送转/现金分红/股息率（按年度合并统计）
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import pandas as pd
from core import get_a_dividend_detail, analyze_dividend_consistency, calculate_dividend_metrics, get_yearly_dividend_summary


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <股票代码>")
        sys.exit(1)

    stock_code = sys.argv[1]
    print("=" * 60)
    print(f"股票: {stock_code} 分红配送分析（年度合并统计）")
    print("=" * 60)

    # ── 原始数据预览 ──
    df = get_a_dividend_detail(stock_code)
    if df.empty:
        print("\n[X] 获取分红数据失败")
        return

    cols = ["报告期", "现金分红-现金分红比例", "现金分红-股息率", "送转股份-送转总比例"]
    available = [c for c in cols if c in df.columns]
    print(f"\n>> 原始分红记录: 共 {len(df)} 条\n")
    if available:
        print(df[available].head(10).to_string(index=False))

    # ── 按年度合并统计 ──
    print(f"\n>> 按年度合并分红统计")
    print(f"  (同一年多次分红合并为年度合计，每10股金额 ÷10 = 每股金额)")
    yearly = get_yearly_dividend_summary(stock_code)
    if not yearly.empty:
        print()
        yearly_display = yearly.copy()
        yearly_display["股息率"] = yearly_display["股息率"].apply(
            lambda x: f"{x:.2f}%" if pd.notna(x) else "--"
        )
        yearly_display["每股合计"] = yearly_display["每股合计"].apply(
            lambda x: f"{x:.4f}" if pd.notna(x) else "--"
        )
        yearly_display["每10股合计"] = yearly_display["每10股合计"].apply(
            lambda x: f"{x:.2f}" if pd.notna(x) else "--"
        )
        print(yearly_display.to_string(index=False))
    else:
        print("  [无有效分红数据]")

    # ── 股息率指标（基于最近完整年度） ──
    print(f"\n>> 股息率计算")
    metrics = calculate_dividend_metrics(stock_code, {})
    if metrics.get("股息率") is not None:
        print(f"  股息率: {metrics['股息率']}%")
        if metrics.get("股息率_计算依据"):
            print(f"  计算依据: {metrics['股息率_计算依据']}")
        if metrics.get("股息率解读"):
            print(f"  解读: {metrics['股息率解读']}")
    else:
        print("  [计算股息率需要股价数据，传参如: python main.py 000858 144]")
        if len(sys.argv) >= 3:
            try:
                price = float(sys.argv[2])
                metrics_with_price = calculate_dividend_metrics(stock_code, {"现价": price})
                if metrics_with_price.get("股息率") is not None:
                    print(f"  股息率: {metrics_with_price['股息率']}%")
                    if metrics_with_price.get("股息率_计算依据"):
                        print(f"  计算依据: {metrics_with_price['股息率_计算依据']}")
            except (ValueError, TypeError):
                pass

    if metrics.get("股利支付率") is not None:
        print(f"\n  股利支付率: {metrics['股利支付率']}%")
        if metrics.get("股利支付率解读"):
            print(f"  解读: {metrics['股利支付率解读']}")

    if metrics.get("派现融资比") is not None:
        print(f"\n  派现融资比: {metrics['派现融资比']}%")
        if metrics.get("派现融资比解读"):
            print(f"  解读: {metrics['派现融资比解读']}")

    # ── 分红连续性 ──
    consistency = analyze_dividend_consistency(df)
    if "error" not in consistency:
        print(f"\n>> 分红连续性")
        print(f"  现金分红年份: {consistency['years_with_cash_dividend']}")
        print(f"  评价: {consistency['consistency']}")

    print(f"\n{'=' * 60}")
    print("数据来源: 东方财富")
    print("=" * 60)


if __name__ == "__main__":
    main()
