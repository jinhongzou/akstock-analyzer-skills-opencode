# -*- coding: utf-8 -*-
"""
国家队ETF持仓规模追踪器

数据源: Tushare fund_share（日频份额数据）

追踪汇金系重仓的核心宽基ETF的份额变化，
反映国家队入场/退出的整体规模方向。

使用方式:
    from core.src.analyzers import NationalTeamFundTracker
    tracker = NationalTeamFundTracker()
    data = tracker.get_monthly_summary("20250101", "20260630")
"""
import os
import pandas as pd
from typing import Optional


class NationalTeamFundTracker:
    """国家队ETF持仓规模追踪器

    基于Tushare fund_share接口，获取汇金系重仓的核心宽基ETF
    的每日份额数据，按月汇总。

    数据频率: 日频（按月取月末值）
    单位: fd_share 为万份
    """

    # 汇金系重仓的核心宽基ETF（来源：2025年报披露的汇金持仓）
    # (ts_code, name, 跟踪指数)
    CORE_ETFS = [
        ("510300.SH", "华泰柏瑞沪深300ETF", "沪深300"),
        ("510050.SH", "华夏上证50ETF", "上证50"),
        ("510310.SH", "易方达沪深300ETF", "沪深300"),
        ("510330.SH", "华夏沪深300ETF", "沪深300"),
        ("159919.SZ", "嘉实沪深300ETF", "沪深300"),
        ("159845.SZ", "南方中证1000ETF", "中证1000"),
        ("512100.SH", "南方中证1000ETF", "中证1000"),
        ("588000.SH", "华夏上证科创板50ETF", "科创50"),
    ]

    # 扩展ETF列表（用于市场对比，非汇金重仓）
    MARKET_ETFS = [
        ("159915.SZ", "易方达创业板ETF", "创业板指"),
        ("510500.SH", "南方中证500ETF", "中证500"),
        ("512880.SH", "国泰中证全指证券公司ETF", "证券公司"),
    ]

    def __init__(self):
        self._ts_api = None

    # ══════════════════════════════════════════
    # Tushare API
    # ══════════════════════════════════════════

    def _get_ts_api(self):
        """获取Tushare Pro API实例"""
        if self._ts_api is not None:
            return self._ts_api
        token = self._get_token()
        if token:
            import tushare as ts
            ts.set_token(token)
            self._ts_api = ts.pro_api()
        return self._ts_api

    @staticmethod
    def _get_token() -> str:
        """从环境变量读取TUSHARE_TOKEN"""
        token = os.environ.get("TUSHARE_TOKEN", "")
        if token:
            return token
        env_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TUSHARE_TOKEN"):
                        return line.split("=", 1)[1].strip()
        except (FileNotFoundError, IOError):
            pass
        return ""

    # ══════════════════════════════════════════
    # 单只ETF数据
    # ══════════════════════════════════════════

    def get_etf_daily_shares(self, ts_code: str, start_date: str = "20250101",
                             end_date: str = "20260630") -> pd.DataFrame:
        """获取单只ETF的日频份额数据

        Args:
            ts_code: Tushare代码，如 "510300.SH"
            start_date: 起始日期 YYYYMMDD
            end_date: 截止日期 YYYYMMDD

        Returns:
            DataFrame包含: trade_date, fd_share(万份), fund_type, market
            已按trade_date升序排列
        """
        api = self._get_ts_api()
        if api is None:
            return pd.DataFrame()

        df = api.fund_share(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return pd.DataFrame()

        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["fd_share"] = df["fd_share"].astype(float)
        df = df.sort_values("trade_date").reset_index(drop=True)
        return df

    # ══════════════════════════════════════════
    # 月度汇总
    # ══════════════════════════════════════════

    def get_etf_monthly_shares(self, ts_code: str, start_date: str = "20250101",
                               end_date: str = "20260630") -> pd.DataFrame:
        """获取单只ETF的月末份额

        按月分组，取每月最后一个交易日的份额值。

        Returns:
            DataFrame: [month(Period), fd_share(万份)]
            已按month升序排列
        """
        df = self.get_etf_daily_shares(ts_code, start_date, end_date)
        if df.empty:
            return pd.DataFrame()

        df["month"] = df["trade_date"].dt.to_period("M")
        monthly = df.groupby("month", sort=False).last().reset_index()
        monthly = monthly.sort_values("month")[["month", "fd_share"]]
        return monthly

    def get_multi_etf_monthly(self, etf_list: list = None,
                              start_date: str = "20250101",
                              end_date: str = "20260630") -> dict:
        """获取多只ETF的月末份额

        Args:
            etf_list: ETF列表，每项为(ts_code, name, index_name)，
                      默认使用CORE_ETFS
            start_date: 起始日期
            end_date: 截止日期

        Returns:
            {ts_code: {name, index, monthly: DataFrame}, ...}
        """
        if etf_list is None:
            etf_list = self.CORE_ETFS

        results = {}
        for ts_code, name, index_name in etf_list:
            monthly = self.get_etf_monthly_shares(ts_code, start_date, end_date)
            if not monthly.empty:
                results[ts_code] = {
                    "name": name,
                    "index": index_name,
                    "monthly": monthly,
                }
        return results

    # ══════════════════════════════════════════
    # 汇总报告
    # ══════════════════════════════════════════

    def get_monthly_summary(self, start_date: str = "20250101",
                            end_date: str = "20260630",
                            etf_list: list = None) -> dict:
        """获取逐月汇总报告

        Args:
            start_date: 起始日期 YYYYMMDD
            end_date: 截止日期 YYYYMMDD
            etf_list: ETF列表，默认CORE_ETFS

        Returns:
            {
                months: ["2025-01", ...],
                series: [{month, total, change, change_pct, ...}, ...],
                etf_details: {ts_code: {name, values: [{month, fd_share}, ...]}},
                summary: {first_total, last_total, total_change, total_change_pct},
            }
        """
        results = self.get_multi_etf_monthly(etf_list, start_date, end_date)
        if not results:
            return {"months": [], "series": [], "etf_details": {}, "summary": {}}

        # 收集所有月份
        all_months = sorted(set(
            str(m) for r in results.values()
            for m in r["monthly"]["month"].unique()
        ))

        # 构建明细
        etf_details = {}
        for ts_code, data in results.items():
            records = []
            for _, row in data["monthly"].iterrows():
                records.append({
                    "month": str(row["month"]),
                    "fd_share": float(row["fd_share"]),
                })
            etf_details[ts_code] = {
                "name": data["name"],
                "index": data["index"],
                "values": records,
            }

        # 构建时序
        series = []
        prev_total = None
        for month in all_months:
            row_total = 0.0
            for ts_code, data in results.items():
                sub = data["monthly"][data["monthly"]["month"].astype(str) == month]
                if not sub.empty:
                    row_total += float(sub.iloc[0]["fd_share"])

            entry = {"month": month, "total": row_total}
            if prev_total is not None:
                entry["change"] = row_total - prev_total
                entry["change_pct"] = round((row_total - prev_total) / prev_total * 100, 2)
            else:
                entry["change"] = 0
                entry["change_pct"] = 0.0
            series.append(entry)
            prev_total = row_total

        # 汇总
        if series:
            summary = {
                "first_month": series[0]["month"],
                "last_month": series[-1]["month"],
                "first_total": series[0]["total"],
                "last_total": series[-1]["total"],
                "total_change": series[-1]["total"] - series[0]["total"],
                "total_change_pct": round(
                    (series[-1]["total"] - series[0]["total"]) / series[0]["total"] * 100, 2
                ),
                "etf_count": len(results),
            }
        else:
            summary = {}

        return {
            "months": all_months,
            "series": series,
            "etf_details": etf_details,
            "summary": summary,
        }

    # ══════════════════════════════════════════
    # NAV 交叉验证
    # ══════════════════════════════════════════

    def get_etf_nav_check(self, ts_code: str, start_date: str = "20250101",
                          end_date: str = "20260630") -> pd.DataFrame:
        """获取ETF份额与NAV的交叉验证数据

        合并 fund_share 和 fund_nav，返回原始数据供调用方自行分析。
        可用 share_change_pct 与 nav_change_pct 对比:
          份额↓+NAV稳定=真实赎回，份额↓+NAV↑=份额合并。

        Returns:
            DataFrame: [date, fd_share(万份), unit_nav(元), total_mv(亿元)]
        """
        api = self._get_ts_api()
        if api is None:
            return pd.DataFrame()

        df_s = api.fund_share(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df_n = api.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df_s is None or df_s.empty or df_n is None or df_n.empty:
            return pd.DataFrame()

        df_s["trade_date"] = pd.to_datetime(df_s["trade_date"])
        df_n["nav_date"] = pd.to_datetime(df_n["nav_date"])
        df_s["fd_share"] = df_s["fd_share"].astype(float)
        df_n["unit_nav"] = df_n["unit_nav"].astype(float)

        merged = pd.merge(
            df_s[["trade_date", "fd_share"]].rename(columns={"trade_date": "date"}),
            df_n[["nav_date", "unit_nav"]].rename(columns={"nav_date": "date"}),
            on="date", how="inner",
        )
        merged = merged.sort_values("date").reset_index(drop=True)
        merged["total_mv_yi"] = (merged["fd_share"] * merged["unit_nav"] / 10000).round(2)
        return merged

    def verify_drop_is_real(self, ts_code: str, before_date: str,
                            after_date: str) -> dict:
        """获取特定时间窗口内份额与NAV的变化数据

        提供份额变化率和NAV变化率，由调用方自行判断。
        判断依据: NAV稳定+份额下降=真实赎回；NAV翻倍=份额合并。

        Args:
            ts_code: ETF代码
            before_date: 变化前日期 YYYYMMDD
            after_date: 变化后日期 YYYYMMDD

        Returns:
            {
                before: {date, fd_share, unit_nav, total_mv},
                after: {date, fd_share, unit_nav, total_mv},
                share_change_pct: float,
                nav_change_pct: float,
            }
        """
        df = self.get_etf_nav_check(ts_code, before_date, after_date)
        if df.empty or len(df) < 2:
            return {"error": "数据不足"}

        before = df.iloc[0]
        after = df.iloc[-1]
        share_pct = (after["fd_share"] / before["fd_share"] - 1) * 100
        nav_pct = (after["unit_nav"] / before["unit_nav"] - 1) * 100

        return {
            "before": {
                "date": str(before["date"].date()),
                "fd_share": float(before["fd_share"]),
                "unit_nav": float(before["unit_nav"]),
                "total_mv_yi": float(before["total_mv_yi"]),
            },
            "after": {
                "date": str(after["date"].date()),
                "fd_share": float(after["fd_share"]),
                "unit_nav": float(after["unit_nav"]),
                "total_mv_yi": float(after["total_mv_yi"]),
            },
            "share_change_pct": round(share_pct, 2),
            "nav_change_pct": round(nav_pct, 2),
        }

    # ══════════════════════════════════════════
    # 辅助: 打印报告（命令行查看用）
    # ══════════════════════════════════════════

    def print_summary(self, start_date: str = "20250101",
                      end_date: str = "20260630"):
        """打印月度汇总到终端"""
        data = self.get_monthly_summary(start_date, end_date)
        if not data["series"]:
            print("无数据")
            return

        print(f"\n{'月份':<10}", end="")
        for info in data["etf_details"].values():
            print(f"  {info['name'][:10]:>12}", end="")
        print(f"  {'合计(万份)':>14}  {'环比':>12}")

        print("-" * 160)
        for entry in data["series"]:
            print(f"{entry['month']:<10}", end="")
            for ts_code, info in data["etf_details"].items():
                found = [v for v in info["values"] if v["month"] == entry["month"]]
                if found:
                    print(f"  {found[0]['fd_share']:>12,.0f}", end="")
                else:
                    print(f"  {'---':>12}", end="")

            if entry["month"] == data["months"][0]:
                print(f"  {entry['total']:>14,.0f}  {'(基期)':>12}")
            else:
                print(f"  {entry['total']:>14,.0f}  {entry['change']:>+12,.0f} ({entry['change_pct']:+.2f}%)")

        s = data["summary"]
        print(f"\n统计区间: {s['first_month']} ~ {s['last_month']}")
        print(f"总规模: {s['first_total']:,.0f} -> {s['last_total']:,.0f} "
              f"(变化 {s['total_change']:+,.0f} 万份, {s['total_change_pct']:+.2f}%)")
