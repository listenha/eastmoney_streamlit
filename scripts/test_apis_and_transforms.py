#!/usr/bin/env python3
"""
测试脚本：验证API接口可用性和transform逻辑正确性

用法：
    python scripts/test_apis_and_transforms.py
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from eastmoney_tool.datacenter import EastMoneyDataCenter
from eastmoney_tool.sources.seat_track import build_params as seat_params, CYCLE_1M, CYCLE_3M, CYCLE_6M
from eastmoney_tool.sources.trade_daily import build_params as trade_params
from eastmoney_tool.sources.survey import build_params as survey_params
from eastmoney_tool.transforms.topk import topk
from eastmoney_tool.transforms.set_ops import intersect_by_key
from eastmoney_tool.transforms.trade_filters import filter_netbuy_ratio


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_api_survey():
    """测试表一API：机构调研统计"""
    print_section("测试表一API：机构调研统计 (RPT_ORG_SURVEYNEW)")
    
    dc = EastMoneyDataCenter()
    today = dt.date.today()
    date_gt = (today - dt.timedelta(days=7)).strftime("%Y-%m-%d")
    
    params = survey_params(receive_start_date_gt=date_gt, page_size=10)
    print(f"请求参数: {params}\n")
    
    try:
        df = dc.get_result_df(params)
        print(f"✓ API调用成功")
        print(f"  返回行数: {len(df)}")
        print(f"  列名: {list(df.columns)}")
        print(f"\n前3行数据预览:")
        print(df.head(3).to_string())
        
        # 检查关键字段
        required_cols = ['SECURITY_CODE', 'SECURITY_NAME_ABBR', 'SUM']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            print(f"\n⚠ 警告: 缺少关键字段: {missing}")
        else:
            print(f"\n✓ 关键字段存在: {required_cols}")
        
        # 测试排序（按SUM降序）
        if 'SUM' in df.columns and len(df) > 0:
            df_sorted = df.sort_values('SUM', ascending=False, kind='mergesort')
            print(f"\n✓ 排序测试: 已按SUM降序排序")
            print(f"  SUM最大值: {df_sorted.iloc[0]['SUM'] if len(df_sorted) > 0 else 'N/A'}")
        
        return df
    except Exception as e:
        print(f"✗ API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_api_seat():
    """测试表二API：机构席位追踪"""
    print_section("测试表二API：机构席位追踪 (RPT_ORGANIZATION_SEATNEW)")
    
    dc = EastMoneyDataCenter()
    
    for cycle in [CYCLE_1M, CYCLE_3M, CYCLE_6M]:
        print(f"\n测试周期: {cycle.label} (code={cycle.code})")
        params = seat_params(cycle=cycle, page_size=20)
        print(f"请求参数: {params}\n")
        
        try:
            df = dc.get_result_df(params)
            print(f"✓ API调用成功")
            print(f"  返回行数: {len(df)}")
            print(f"  列名: {list(df.columns)}")
            
            # 查找可能的净买额和买入次数字段
            netbuy_candidates = [c for c in df.columns if 'NET' in c.upper() and 'BUY' in c.upper()]
            buycnt_candidates = [c for c in df.columns if 'BUY' in c.upper() and ('TIME' in c.upper() or 'CNT' in c.upper())]
            onlist_candidates = [c for c in df.columns if 'ONLIST' in c.upper()]
            
            print(f"\n可能的净买额字段: {netbuy_candidates}")
            print(f"可能的买入次数字段: {buycnt_candidates}")
            print(f"ONLIST相关字段: {onlist_candidates}")
            
            if len(df) > 0:
                print(f"\n前2行数据预览:")
                print(df.head(2).to_string())
            
            if cycle == CYCLE_1M:  # 只对第一个周期做详细分析
                return df
        except Exception as e:
            print(f"✗ API调用失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    return None


def test_api_trade():
    """测试表三API：机构买卖每日统计"""
    print_section("测试表三API：机构买卖每日统计 (RPT_ORGANIZATION_TRADE_DETAILSNEW)")
    
    dc = EastMoneyDataCenter()
    today = dt.date.today()
    date_gte = (today - dt.timedelta(days=5)).strftime("%Y-%m-%d")
    
    params = trade_params(trade_date_gte=date_gte, page_size=20)
    print(f"请求参数: {params}\n")
    
    try:
        df = dc.get_result_df(params)
        print(f"✓ API调用成功")
        print(f"  返回行数: {len(df)}")
        print(f"  列名: {list(df.columns)}")
        
        # 查找可能的占比字段
        ratio_candidates = [c for c in df.columns if 'RATIO' in c.upper() or 'PERCENT' in c.upper() or '%' in c]
        netbuy_candidates = [c for c in df.columns if 'NET' in c.upper() and 'BUY' in c.upper()]
        total_candidates = [c for c in df.columns if 'TOTAL' in c.upper() and 'AMT' in c.upper()]
        
        print(f"\n可能的占比字段: {ratio_candidates}")
        print(f"可能的净买额字段: {netbuy_candidates}")
        print(f"可能的总成交额字段: {total_candidates}")
        
        if len(df) > 0:
            print(f"\n前2行数据预览:")
            print(df.head(2).to_string())
            
            # 如果存在占比字段，测试过滤
            if ratio_candidates:
                ratio_col = ratio_candidates[0]
                print(f"\n测试占比过滤 (使用字段: {ratio_col})")
                df_filtered = filter_netbuy_ratio(df, ratio_col=ratio_col, threshold=10.0)
                print(f"  过滤前: {len(df)} 行")
                print(f"  过滤后 (>10%): {len(df_filtered)} 行")
        
        return df
    except Exception as e:
        print(f"✗ API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_transform_t2(df_seat):
    """测试表二transform：Top10交集"""
    print_section("测试表二Transform：Top10交集逻辑")
    
    if df_seat is None or len(df_seat) == 0:
        print("✗ 需要先获取机构席位追踪数据")
        return None, None, None
    
    # 自动检测字段名
    netbuy_col = None
    buycnt_col = None
    
    # 尝试找到净买额字段
    for col in df_seat.columns:
        if 'NET' in col.upper() and 'BUY' in col.upper() and 'AMT' in col.upper():
            netbuy_col = col
            break
    
    # 尝试找到买入次数字段
    for col in df_seat.columns:
        if ('BUY' in col.upper() and 'TIME' in col.upper()) or ('ONLIST' in col.upper() and 'TIME' in col.upper()):
            buycnt_col = col
            break
    
    if not netbuy_col or not buycnt_col:
        print(f"⚠ 无法自动检测字段名")
        print(f"  可用字段: {list(df_seat.columns)}")
        print(f"  请手动指定 netbuy_col 和 buycnt_col")
        return None, None, None
    
    print(f"使用字段:")
    print(f"  净买额: {netbuy_col}")
    print(f"  买入次数: {buycnt_col}")
    
    try:
        # Top10 by 净买额
        top10_netbuy = topk(df_seat, netbuy_col, k=10, ascending=False)
        print(f"\n✓ Top10 by {netbuy_col}: {len(top10_netbuy)} 行")
        
        # Top10 by 买入次数
        top10_buycnt = topk(df_seat, buycnt_col, k=10, ascending=False)
        print(f"✓ Top10 by {buycnt_col}: {len(top10_buycnt)} 行")
        
        # 交集
        key_col = 'SECURITY_CODE'
        inter = intersect_by_key(top10_netbuy, top10_buycnt, key=key_col)
        print(f"✓ 交集结果: {len(inter)} 行")
        
        if len(inter) > 0:
            print(f"\n交集股票代码: {inter[key_col].tolist()}")
        
        return top10_netbuy, top10_buycnt, inter
    except Exception as e:
        print(f"✗ Transform失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def test_transform_t3(df_trade):
    """测试表三transform：多窗口去重合并"""
    print_section("测试表三Transform：多窗口去重合并逻辑")
    
    if df_trade is None:
        print("✗ 需要先获取机构买卖每日统计数据")
        return None
    
    dc = EastMoneyDataCenter()
    today = dt.date.today()
    
    windows = [
        ("today", 0),
        ("3d", 3),
        ("5d", 5),
        ("10d", 10),
        ("1m", 30),
    ]
    
    # 查找占比字段
    ratio_col = None
    for col in df_trade.columns:
        if 'RATIO' in col.upper() or 'PERCENT' in col.upper():
            ratio_col = col
            break
    
    if not ratio_col:
        print(f"⚠ 无法自动检测占比字段")
        print(f"  可用字段: {list(df_trade.columns)}")
        return None
    
    print(f"使用占比字段: {ratio_col}")
    print(f"阈值: 10.0%\n")
    
    frames = []
    for label, days in windows:
        try:
            date_gte = (today - dt.timedelta(days=days)).strftime("%Y-%m-%d")
            params = trade_params(trade_date_gte=date_gte, page_size=50)
            df = dc.get_result_df(params)
            df_filtered = filter_netbuy_ratio(df, ratio_col=ratio_col, threshold=10.0)
            print(f"  {label:5s} ({days:2d}天): {len(df_filtered)} 行满足条件")
            if not df_filtered.empty:
                frames.append(df_filtered)
        except Exception as e:
            print(f"  {label:5s}: ✗ 失败 - {e}")
    
    if not frames:
        print("\n✗ 没有数据满足条件")
        return None
    
    # 合并并去重
    import pandas as pd
    combined = pd.concat(frames, ignore_index=True)
    key_col = 'SECURITY_CODE'
    
    if key_col in combined.columns:
        deduped = combined.drop_duplicates(subset=[key_col], keep='first')
        print(f"\n✓ 合并后: {len(combined)} 行")
        print(f"✓ 去重后: {len(deduped)} 行 (去重键: {key_col})")
        return deduped
    else:
        print(f"\n⚠ 缺少去重键字段: {key_col}")
        return combined


def main():
    print("="*60)
    print("  东方财富工具：API和Transform测试")
    print("="*60)
    
    # 测试API
    df_survey = test_api_survey()
    df_seat = test_api_seat()
    df_trade = test_api_trade()
    
    # 测试Transform
    if df_seat is not None:
        top10_netbuy, top10_buycnt, inter_t2 = test_transform_t2(df_seat)
    
    if df_trade is not None:
        t3_result = test_transform_t3(df_trade)
    
    print_section("测试完成")
    print("请检查上述输出，确认:")
    print("1. 所有API调用成功")
    print("2. 字段名正确识别")
    print("3. Transform逻辑正确")


if __name__ == "__main__":
    main()

