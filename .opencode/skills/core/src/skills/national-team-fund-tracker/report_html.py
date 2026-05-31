# -*- coding: utf-8 -*-
"""
国家队ETF持仓规模追踪 - HTML图表报告生成

基于 main.py 采集的数据，生成交互式ECharts HTML报告。

用法:
    python .opencode/skills/core/src/skills/national-team-fund-tracker/report_html.py

输出:
    output/national_team_etf_tracker.html
"""
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from core import NationalTeamFundTracker


def _default_date_range(years=10):
    """返回默认起止日期 YYYYMMDD，往前推 years 年"""
    today = datetime.today()
    start = today - timedelta(days=years * 365.25)
    return start.strftime("%Y%m%d"), today.strftime("%Y%m%d")


def fetch_data():
    """获取原始数据，日期范围优先从命令行参数读取"""
    start_date = sys.argv[1] if len(sys.argv) > 1 else None
    end_date = sys.argv[2] if len(sys.argv) > 2 else None
    if not start_date or not end_date:
        start_date, end_date = _default_date_range(10)
    tracker = NationalTeamFundTracker()
    return tracker.get_monthly_summary(start_date, end_date)


def _format_num(v):
    return round(v, 0)


def _table_rows(months, totals, changes, etf_series_data):
    """生成HTML表格行"""
    rows = []
    for i, month in enumerate(months):
        cells = [f"<td>{month}</td>"]
        for name in etf_series_data:
            v = etf_series_data[name][i]
            cells.append(f"<td>{v:,.0f}</td>" if v is not None else "<td>---</td>")
        cells.append(f"<td style='font-weight:600'>{totals[i]:,.0f}</td>")
        if i == 0:
            cells.append("<td style='color:#999'>(基期)</td>")
        else:
            c = "#26a69a" if changes[i] >= 0 else "#ef5350"
            cells.append(f"<td style='color:{c}'>{changes[i]:+.2f}%</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "\n".join(rows)


def generate_html(data, output_path):
    """生成交互式HTML图表报告"""
    series = data["series"]
    details = data["etf_details"]
    summary = data["summary"]

    months = [s["month"] for s in series]
    totals = [_format_num(s["total"]) for s in series]
    changes = [s.get("change_pct", 0) for s in series]

    first_total = summary.get("first_total", 0)
    last_total = summary.get("last_total", 0)
    total_change_pct = summary.get("total_change_pct", 0)

    # 各ETF月度数据
    etf_names = []
    etf_series_data = {}
    for code in ["510300.SH", "510050.SH", "510310.SH", "510330.SH",
                  "159919.SZ", "159845.SZ", "512100.SH", "588000.SH"]:
        if code in details:
            name = details[code]["name"]
            etf_names.append(name)
            vals = []
            for m in months:
                found = [v for v in details[code]["values"] if v["month"] == m]
                vals.append(_format_num(found[0]["fd_share"]) if found else None)
            etf_series_data[name] = vals

    # 最新月度结构
    last = series[-1]["month"]
    pie_categories = {}
    for code, cat in [
        ("510300.SH", "沪深300"), ("510310.SH", "沪深300"), ("510330.SH", "沪深300"), ("159919.SZ", "沪深300"),
        ("510050.SH", "上证50"),
        ("588000.SH", "科创50"),
        ("159845.SZ", "中证1000"), ("512100.SH", "中证1000"),
    ]:
        if code in details:
            found = [v for v in details[code]["values"] if v["month"] == last]
            if found:
                pie_categories[cat] = pie_categories.get(cat, 0) + found[0]["fd_share"]

    months_json = json.dumps(months)
    totals_json = json.dumps([round(t, 0) for t in totals])
    changes_json = json.dumps(changes)

    # ETF折线系列
    etf_series_parts = []
    legend_names = []
    colors = ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272", "#fc8452", "#9a60b4"]
    for i, (name, vals) in enumerate(etf_series_data.items()):
        short = name[:10]
        legend_names.append(short)
        cleaned = ["null" if v is None else str(round(v, 0)) for v in vals]
        etf_series_parts.append(f"""{{
        name: '{short}',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: {{ width: 2 }},
        itemStyle: {{ color: '{colors[i % len(colors)]}' }},
        data: [{','.join(cleaned)}]
    }}""")

    etf_series_str = ",\n      ".join(etf_series_parts)
    legend_names_str = json.dumps(legend_names, ensure_ascii=False)

    # 饼图数据
    pie_items = [{"name": k, "value": round(v, 0)} for k, v in sorted(pie_categories.items())]
    pie_json = json.dumps(pie_items, ensure_ascii=False)

    # 表格
    table_rows = _table_rows(months, totals, changes, etf_series_data)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>国家队ETF持仓规模追踪</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #f5f7fa; font-family: -apple-system, 'Microsoft YaHei', sans-serif; padding: 20px; }}
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #fff; padding: 30px 40px; border-radius: 12px; margin-bottom: 24px; }}
.header h1 {{ font-size: 24px; font-weight: 600; }}
.header p {{ color: #8899b4; margin-top: 8px; font-size: 14px; }}
.header .stats {{ display: flex; gap: 32px; margin-top: 20px; flex-wrap: wrap; }}
.header .stat-item .num {{ font-size: 28px; font-weight: 700; }}
.header .stat-item .num.down {{ color: #ef5350; }}
.header .stat-item .num.up {{ color: #26a69a; }}
.header .stat-item .label {{ font-size: 12px; color: #8899b4; margin-top: 2px; }}
.chart-box {{ background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.chart-box h2 {{ font-size: 16px; color: #333; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #f0f0f0; }}
.chart {{ width: 100%; height: 400px; }}
.chart-sm {{ height: 320px; }}
.grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }}
@media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
th {{ background: #f8f9fb; color: #666; font-weight: 500; padding: 8px 6px; text-align: right; border-bottom: 2px solid #e8e8e8; white-space: nowrap; }}
th:first-child {{ text-align: left; }}
td {{ padding: 6px; text-align: right; border-bottom: 1px solid #f0f0f0; font-variant-numeric: tabular-nums; }}
td:first-child {{ text-align: left; color: #333; font-weight: 500; }}
tr:hover td {{ background: #f8f9fb; }}
.footer {{ text-align: center; color: #999; font-size: 12px; padding: 20px; }}
</style>
</head>
<body>

<div class="header">
  <h1>国家队ETF持仓规模追踪</h1>
  <p>数据源: Tushare fund_share（日频份额，取月末值） · 追踪标的: 汇金系重仓8只核心宽基ETF</p>
  <p>统计区间: {summary.get('first_month', '-')} ~ {summary.get('last_month', '-')}</p>
  <div class="stats">
    <div class="stat-item">
      <div class="num {'down' if total_change_pct < 0 else 'up'}">{last_total / 10000:,.1f}<span style="font-size:14px;color:#8899b4"> 亿份</span></div>
      <div class="label">最新月末总份额</div>
    </div>
    <div class="stat-item">
      <div class="num {'down' if total_change_pct < 0 else 'up'}">{total_change_pct:+.2f}%</div>
      <div class="label">累计变化</div>
    </div>
    <div class="stat-item">
      <div class="num" style="color:#8899b4">{first_total / 10000:,.1f}<span style="font-size:14px;color:#8899b4"> → {last_total / 10000:,.1f} 亿份</span></div>
      <div class="label">基期 → 最新</div>
    </div>
  </div>
</div>

<div class="grid">
  <div class="chart-box">
    <h2>月度总份额趋势</h2>
    <div id="chart-total" class="chart"></div>
  </div>
  <div class="chart-box">
    <h2>最新月度结构</h2>
    <div id="chart-pie" class="chart chart-sm"></div>
  </div>
</div>

<div class="chart-box">
  <h2>各ETF份额变化趋势</h2>
  <div id="chart-etfs" class="chart"></div>
</div>

<div class="chart-box">
  <h2>月度环比变化</h2>
  <div id="chart-change" class="chart chart-sm"></div>
</div>

<div class="chart-box">
  <h2>逐月数据明细</h2>
  <div style="overflow-x:auto">
  <table>
    <thead>
      <tr>
        <th>月份</th>
        {''.join(f'<th>{n[:8]}</th>' for n in etf_names)}
        <th>合计(万份)</th>
        <th>环比</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
  </div>
</div>

<div class="footer">
  数据来源: Tushare Pro · 注意: fd_share为ETF总份额(万份)，非汇金单独持仓<br>
  本报告仅供参考，不构成投资建议
</div>

<script>
var months = {months_json};
var totals = {totals_json};
var changes = {changes_json};

// Chart 1: 总份额趋势
var chart1 = echarts.init(document.getElementById('chart-total'));
chart1.setOption({{
  tooltip: {{ trigger: 'axis', formatter: function(p) {{ return p[0].axisValue + '<br/>合计: ' + (p[0].value / 10000).toFixed(1) + ' 亿份'; }} }},
  grid: {{ left: 60, right: 20, bottom: 30, top: 20 }},
  xAxis: {{ type: 'category', data: months, axisLabel: {{ rotate: 45, fontSize: 11 }} }},
  yAxis: {{ type: 'value', name: '万份', axisLabel: {{ formatter: function(v) {{ return (v/10000) + '亿'; }} }} }},
  series: [{{
    type: 'line', smooth: true, data: totals,
    lineStyle: {{ width: 3, color: '#5470c6' }},
    itemStyle: {{ color: '#5470c6' }},
    areaStyle: {{ color: {{ type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
      colorStops: [{{offset:0,color:'rgba(84,112,198,0.3)'}},{{offset:1,color:'rgba(84,112,198,0.02)'}}] }} }},
    markPoint: {{ data: [{{ type: 'max', name: '最大值' }}, {{ type: 'min', name: '最小值' }}] }}
  }}]
}});

// Chart 2: 各ETF趋势
var chart2 = echarts.init(document.getElementById('chart-etfs'));
chart2.setOption({{
  tooltip: {{ trigger: 'axis' }},
  legend: {{ data: {legend_names_str}, top: 0, left: 'center', type: 'scroll' }},
  grid: {{ left: 60, right: 20, bottom: 30, top: 50 }},
  xAxis: {{ type: 'category', data: months, axisLabel: {{ rotate: 45, fontSize: 11 }} }},
  yAxis: {{ type: 'value', name: '万份', axisLabel: {{ formatter: function(v) {{ return (v/10000) + '亿'; }} }} }},
  series: [{etf_series_str}]
}});

// Chart 3: 环比变化
var chart3 = echarts.init(document.getElementById('chart-change'));
chart3.setOption({{
  tooltip: {{ trigger: 'axis', formatter: function(p) {{ return p[0].axisValue + '<br/>环比: ' + (p[0].value != null ? p[0].value.toFixed(2) + '%' : '基期'); }} }},
  grid: {{ left: 60, right: 20, bottom: 30, top: 20 }},
  xAxis: {{ type: 'category', data: months, axisLabel: {{ rotate: 45, fontSize: 11 }} }},
  yAxis: {{ type: 'value', name: '%', axisLabel: {{ formatter: '{{value}}%' }} }},
  series: [{{
    type: 'bar', barWidth: '60%',
    data: changes.map(function(v, i) {{
      if (i === 0) return {{ value: 0, itemStyle: {{ color: '#ccc' }} }};
      return {{ value: v, itemStyle: {{ color: v >= 0 ? '#26a69a' : '#ef5350' }} }};
    }}),
    markLine: {{ data: [{{ yAxis: 0 }}], lineStyle: {{ type: 'dashed', color: '#999' }} }},
    markPoint: {{ data: [{{ type: 'max', name: '最大增幅' }}, {{ type: 'min', name: '最大降幅' }}] }}
  }}]
}});

// Chart 4: 饼图
var chart4 = echarts.init(document.getElementById('chart-pie'));
var pieData = {pie_json};
chart4.setOption({{
  tooltip: {{ formatter: function(p) {{ return p.name + '<br/>' + (p.value / 10000).toFixed(1) + ' 亿份 (' + p.percent.toFixed(1) + '%)'; }} }},
  series: [{{
    type: 'pie', radius: ['40%', '70%'],
    data: pieData,
    label: {{ formatter: '{{b}}\\n{{d}}%', fontSize: 12 }},
    itemStyle: {{ borderRadius: 6 }},
    emphasis: {{ label: {{ fontSize: 14 }}, itemStyle: {{ shadowBlur: 10 }} }}
  }}]
}});
</script>
</body>
</html>"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML图表报告已生成: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    data = fetch_data()
    if not data["series"]:
        print("无数据")
        sys.exit(1)
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", "output")
    output_path = os.path.join(output_dir, "national_team_etf_tracker.html")
    generate_html(data, output_path)
