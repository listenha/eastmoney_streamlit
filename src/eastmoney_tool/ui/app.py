from __future__ import annotations

import pandas as pd
import streamlit as st

from eastmoney_tool.datacenter import EastMoneyDataCenter
from eastmoney_tool.sources.seat_track import CYCLE_1M, CYCLE_3M, CYCLE_6M
from eastmoney_tool.sources.survey import RANGE_1W, RANGE_1M
from eastmoney_tool.tables.t1_survey import get_survey_data
from eastmoney_tool.tables.t2_seat import get_seat_topk_intersection
from eastmoney_tool.tables.t3_trade import get_trade_netbuy_ratio_filtered
from eastmoney_tool.tables.t4_intersection import get_trade_x_seat_intersection
from eastmoney_tool.ui.formatting import format_amount_to_wan


st.set_page_config(page_title="东方财富机构数据小工具", layout="wide")

st.title("东方财富数据中心：机构数据分析小工具")
st.caption("数据来源：datacenter-web.eastmoney.com（网页背后的结构化接口）。建议合理控制请求频率。")

dc = EastMoneyDataCenter()

tab1, tab2, tab3, tab4 = st.tabs(["表一：机构调研统计", "表二：机构席位追踪", "表三：机构买卖每日统计", "表四：表三 ∩ 表二"])

# -------------------
# 表一：机构调研统计
# -------------------
with tab1:
    st.subheader("表一：机构调研统计（按接待机构数量 SUM 排序）")
    
    colA, colB, colC = st.columns(3)
    with colA:
        range_opt = st.selectbox("时间范围", ["近一周", "近一月"], index=0)
    with colB:
        page_size = st.slider("pageSize", 10, 200, 50, step=10)
    with colC:
        # 根据时间范围设置默认阈值：近一周默认50，近一月默认200
        # 使用组合key，使每个时间范围有独立的阈值设置
        threshold_key = f"t1_sum_threshold_{range_opt}"
        default_threshold = 50 if range_opt == "近一周" else 200
        if threshold_key not in st.session_state:
            st.session_state[threshold_key] = default_threshold
        
        sum_threshold = st.number_input(
            "SUM阈值（只显示SUM > 阈值的数据）",
            min_value=0,
            max_value=1000,
            value=st.session_state[threshold_key],
            step=10,
            key=threshold_key
        )

    range_type = RANGE_1W if range_opt == "近一周" else RANGE_1M

    if st.button("拉取表一数据", key="t1_fetch"):
        with st.spinner("正在获取数据..."):
            df = get_survey_data(dc, range_type=range_type, page_size=page_size)
        
        # 按SUM阈值过滤
        if len(df) > 0 and 'SUM' in df.columns:
            df_filtered = df[df['SUM'] > sum_threshold].copy()
            st.write(f"原始返回行数：{len(df)}；过滤后行数：{len(df_filtered)}（SUM > {sum_threshold}）；时间范围：{range_type.label}")
            
            if len(df_filtered) > 0:
                # 格式化金额字段为万元
                df_display = format_amount_to_wan(df_filtered)
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info(f"未找到SUM > {sum_threshold}的数据")
        else:
            st.write(f"返回行数：{len(df)}；时间范围：{range_type.label}")
            if len(df) > 0:
                # 格式化金额字段为万元
                df_display = format_amount_to_wan(df)
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("未获取到数据")

# -------------------
# 表二：机构席位追踪（Top10交集）
# -------------------
with tab2:
    st.subheader("表二：机构席位追踪（TopK 交集）")
    st.caption("计算方式：TopK by 净买额 ∩ TopK by 买入次数")
    
    cycles = {"近一月": CYCLE_1M, "近三月": CYCLE_3M, "近六月": CYCLE_6M}
    c1, c2, c3 = st.columns(3)
    with c1:
        cycle_label = st.selectbox("统计周期", list(cycles.keys()), index=0)
    with c2:
        k = st.slider("TopK", 5, 50, 10)
    with c3:
        page_size = st.slider("pageSize", 10, 200, 50, step=10, key="t2_pagesize")

    # 默认字段名（已通过API验证）
    col_netbuy = "NET_BUY_AMT"
    col_buycnt = "BUY_TIMES"
    key_col = "SECURITY_CODE"
    
    # 可选：允许用户自定义字段名
    with st.expander("高级选项（字段名配置）", expanded=False):
        col_netbuy = st.text_input("净买额字段名", value=col_netbuy, key="t2_netbuy")
        col_buycnt = st.text_input("买入次数字段名", value=col_buycnt, key="t2_buycnt")
        key_col = st.text_input("交集键（股票代码字段）", value=key_col, key="t2_key")

    if st.button("计算 TopK 交集", key="t2_run"):
        with st.spinner("正在计算..."):
            try:
                top10_netbuy, top10_buycnt, inter = get_seat_topk_intersection(
                    dc,
                    cycle=cycles[cycle_label],
                    k=k,
                    netbuy_col=col_netbuy,
                    buycnt_col=col_buycnt,
                    key_col=key_col,
                    page_size=page_size,
                )
            except Exception as e:
                st.error(f"计算失败：{e}")
                st.stop()

        st.write(f"统计周期：{cycle_label} | TopK：{k}")
        
        cA, cB, cC = st.columns(3)
        with cA:
            st.markdown(f"**Top{k} by 净买额** ({len(top10_netbuy)} 行)")
            st.dataframe(format_amount_to_wan(top10_netbuy), use_container_width=True, height=320)
        with cB:
            st.markdown(f"**Top{k} by 买入次数** ({len(top10_buycnt)} 行)")
            st.dataframe(format_amount_to_wan(top10_buycnt), use_container_width=True, height=320)
        with cC:
            st.markdown(f"**交集结果** ({len(inter)} 行)")
            st.dataframe(format_amount_to_wan(inter), use_container_width=True, height=320)

# -------------------
# 表三：机构买卖每日统计（多窗口去重合并）
# -------------------
with tab3:
    st.subheader("表三：机构买卖每日统计（净买额占比 > 阈值）")
    st.caption("从 {today, 3d, 5d, 10d, 1m} 所有窗口内找出满足条件的股票，去重合并为一个表")

    col1, col2, col3 = st.columns(3)
    with col1:
        threshold = st.slider("净买额占总成交额占比阈值（%）", 0.0, 50.0, 10.0, step=0.5)
    with col2:
        page_size = st.slider("pageSize", 10, 200, 50, step=10, key="t3_pagesize")
    with col3:
        ratio_col = st.text_input("占比字段名", value="RATIO", key="t3_ratio")

    if st.button("生成表三", key="t3_run"):
        with st.spinner("正在从所有窗口获取数据并去重合并..."):
            try:
                df = get_trade_netbuy_ratio_filtered(
                    dc,
                    ratio_col=ratio_col,
                    threshold=threshold,
                    page_size=page_size,
                )
            except Exception as e:
                st.error(f"获取数据失败：{e}")
                st.stop()

        st.write(f"去重后行数：{len(df)}（从所有窗口合并，阈值 > {threshold}%）")
        
        if len(df) > 0:
            # 格式化金额字段为万元
            df_display = format_amount_to_wan(df)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("未找到满足条件的数据")

# -------------------
# 表四：表三 ∩ 表二
# -------------------
with tab4:
    st.subheader("表四：表三 ∩ 表二")
    st.caption("表三（所有窗口的过滤结果）∩ 表二（对应周期的TopK交集）")

    cycles = {"近一月": CYCLE_1M, "近三月": CYCLE_3M, "近六月": CYCLE_6M}
    
    col1, col2 = st.columns(2)
    with col1:
        cycle_label = st.selectbox("表二周期", list(cycles.keys()), index=0, key="t4_cycle")
    with col2:
        page_size = st.slider("pageSize", 10, 200, 50, step=10, key="t4_pagesize")

    # 表三的参数
    with st.expander("表三参数配置", expanded=False):
        t3_threshold = st.slider("表三占比阈值（%）", 0.0, 50.0, 10.0, step=0.5, key="t4_t3_threshold")
        t3_ratio_col = st.text_input("表三占比字段名", value="RATIO", key="t4_t3_ratio")
    
    # 表二的参数
    with st.expander("表二参数配置", expanded=False):
        t2_k = st.slider("表二TopK", 5, 50, 10, key="t4_t2_k")
        t2_netbuy_col = st.text_input("表二净买额字段名", value="NET_BUY_AMT", key="t4_t2_netbuy")
        t2_buycnt_col = st.text_input("表二买入次数字段名", value="BUY_TIMES", key="t4_t2_buycnt")
        key_col = st.text_input("交集键（股票代码字段）", value="SECURITY_CODE", key="t4_key")

    if st.button("计算表四（交集）", key="t4_run"):
        with st.spinner("正在计算表三和表二，并求交集..."):
            try:
                df = get_trade_x_seat_intersection(
                    dc,
                    cycle=cycles[cycle_label],
                    t3_ratio_col=t3_ratio_col,
                    t3_threshold=t3_threshold,
                    t2_k=t2_k,
                    t2_netbuy_col=t2_netbuy_col,
                    t2_buycnt_col=t2_buycnt_col,
                    key_col=key_col,
                    page_size=page_size,
                )
            except Exception as e:
                st.error(f"计算失败：{e}")
                st.stop()

        st.write(f"表二周期：{cycle_label} | 交集行数：{len(df)}")
        
        if len(df) > 0:
            # 格式化金额字段为万元
            df_display = format_amount_to_wan(df)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("表三和表二没有交集，未找到同时满足两个条件的数据")
