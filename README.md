# eastmoney_tool (东方财富数据中心：机构类数据分析小工具)

这是一个面向“东方财富网 / 数据中心”机构数据表格的**轻量数据获取 + 自定义分析 + 表格展示**工具。
我们不做传统的“爬 HTML”，而是直接调用网页背后的结构化接口：
`https://datacenter-web.eastmoney.com/api/data/v1/get`

目标用户：任何希望在东方财富页面基础上做更复杂分析的人。

---

## 任务目标（What we are building）

从东方财富数据中心的多个“机构相关表单”拉取数据（JSON），在本地进行网页未提供的分析操作：
- 排序、筛选、阈值过滤
- TopK（如 Top10）
- 集合运算：并集 / 交集 / 差集（以股票代码 `SECURITY_CODE` 为键）
- 多个时间窗口/多个 tab 的统一聚合

最终输出：
- 可交互表格（Streamlit）
- 可导出 CSV/Parquet（后续可加 Excel）

---

## 使用的接口（Data API）

我们目前使用的接口都是同一种“数据中心通用接口”，仅通过参数区分不同表单：

- Base URL：`https://datacenter-web.eastmoney.com/api/data/v1/get`
- 常见参数：
  - `reportName=...`：表单/报表标识（核心）
  - `columns=ALL` 或指定列
  - `filter=(...)`：过滤条件（东方财富自定义语法）
  - `sortColumns=...&sortTypes=...`：排序字段与升降序
  - `pageNumber/pageSize`：分页
  - `source=WEB&client=WEB`：保持和网页一致
  - `callback=...`：JSONP 回调（**在 Python 中可移除**，直接拿 JSON）

---

## 表单映射（reportName ↔ 东方财富网页/模块）

> 说明：下列“原网页表单”用于帮助你回忆该 reportName 对应的页面功能。
> 我们在代码中以 `reportName` 为唯一事实来源。

1) **机构席位追踪**（你已抓到正确接口）
- reportName：`RPT_ORGANIZATION_SEATNEW`
- 原网页：数据中心 → 股票 → 机构 → “机构席位追踪”
  （你抓包来自：`https://data.eastmoney.com/stock/jgstatistic.html`）

2) **机构买卖每日统计**
- reportName：`RPT_ORGANIZATION_TRADE_DETAILSNEW`
- 原网页：数据中心 → 机构 → “机构买卖每日统计”
- 示例接口（来自你提供的 URL）：
  `...reportName=RPT_ORGANIZATION_TRADE_DETAILSNEW&filter=(TRADE_DATE>='YYYY-MM-DD')`

3) **机构调研统计**
- reportName：`RPT_ORG_SURVEYNEW`
- 原网页：数据中心 → 机构 → “机构调研统计”
- 该表单常见额外参数：`quoteColumns`（用于补充行情字段，如涨跌幅等）

后续若新增表单：只需新增一个 `sources/*.py` 的模块，提供该 reportName 的参数生成逻辑即可。

---

## 我们定义的“自定义表”（Customized Tables）

注意：这些“表”不是东方财富原生表单，而是我们在本地生成的分析结果表。

- `T2_seat_top10_intersection_{cycle}`
  - 表二：机构席位追踪
  - 内容：
    - (Top10 by 机构净买额) ∩ (Top10 by 机构买入次数)
  - cycle ∈ {1m, 3m, 6m}

- `T3_trade_netbuy_ratio`
  - 表三：机构买卖每日统计
  - 内容：从 {today, 3d, 5d, 10d, 1m} 任意窗口内，机构净买额占总成交额占比 > 10% 的股票（去重合并为一个表）

- `T4_trade_x_seat_intersection_{cycle}`
  - 表四：表三 ∩ 表二（以股票代码/名称为键）
  - cycle ∈ {1m, 3m, 6m}
  - 每个 tab：表三（单一结果表）∩ 表二（对应周期）

- `T1_survey_rank_{range}`（计划）
  - 表一：机构调研统计
  - 内容：接待日期近一周/近一月，按“接待机构数量”降序
  - range ∈ {1w, 1m}

---

## 需求列表（你提供的版本，我的理解）

我理解你当前的需求（“交”均指以股票代码或股票名称做交集）：

- [ ] 表一 (x2 tab)：机构调研统计  
  得到接待日期为当前日期近一周 / 近一个月的数据，根据“接待机构数量”降序排序。

- [ ] 表二 (x3 tab)：机构席位追踪  
  机构净买额度前十 ∩ 机构买入次数前十  
  时间窗口：近一月 / 近三月 / 近六月。

- [ ] 表三：机构买卖每日统计  
  从 {today, 3d, 5d, 10d, 1m} 任意窗口内，找出机构净买额占总成交额占比 > 10% 的股票，去重后合并为一个表（不保留窗口标记）。

- [ ] 表四 (x3 tab)：表三 ∩ 表二  
  每个 tab 对应表二的一个周期（近一月/近三月/近六月），计算：表三（单一结果表）∩ 表二（对应周期）。

---

## 代码结构（Modular Design）

- `sources/`：每个“原始表单”的数据获取逻辑（reportName + 参数生成）
  - `seat_track.py`：机构席位追踪（RPT_ORGANIZATION_SEATNEW）
  - `trade_daily.py`：机构买卖每日统计（RPT_ORGANIZATION_TRADE_DETAILSNEW）
  - `survey.py`：机构调研统计（RPT_ORG_SURVEYNEW）

- `transforms/`：分析与聚合逻辑（TopK、交并差、阈值过滤、窗口 union 等）
  - `set_ops.py`：交/并/差
  - `topk.py`：TopK
  - `trade_filters.py`：净买额占比阈值等

- `ui/`：展示层（Streamlit）
  - `app.py`：主入口（页面 + tab + 参数选择 + 表格输出）

- `datacenter.py`：通用请求封装（拼参数、发请求、解析 JSON/JSONP）

---

## 快速开始（Quick Start）

### 1) 安装依赖
```bash
pip install -r requirements.txt
```

### 2) 启动网页
```bash
streamlit run src/eastmoney_tool/ui/app.py
```

---

## 合规与风险提示（Important）
- 本工具调用的是东方财富网页前端同源可访问的数据接口。
- 请合理控制请求频率（内置了简单的节流/缓存接口位点；你也可以加本地缓存）。
- 任何商业化使用前建议确认对方的服务条款与合规要求。

---

## 下一步（Roadmap）
- 完成 4 张表的全部需求逻辑
- 增加本地缓存（SQLite / Parquet）与增量更新
- 增加导出 Excel 与分享链接
- 增加异常重试、接口字段变更的健壮性处理
