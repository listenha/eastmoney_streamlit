#!/usr/bin/env python3
"""
测试脚本：验证所有表的实现函数

用法：
    python scripts/test_table_implementations.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from eastmoney_tool.datacenter import EastMoneyDataCenter
from eastmoney_tool.tables.t1_survey import get_survey_data, RANGE_1W, RANGE_1M
from eastmoney_tool.tables.t2_seat import get_seat_topk_intersection, CYCLE_1M, CYCLE_3M, CYCLE_6M
from eastmoney_tool.tables.t3_trade import get_trade_netbuy_ratio_filtered
from eastmoney_tool.tables.t4_intersection import get_trade_x_seat_intersection


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_t1():
    """测试表一：机构调研统计"""
    print_section("测试表一：机构调研统计")
    
    dc = EastMoneyDataCenter()
    
    for range_type, label in [(RANGE_1W, "近一周"), (RANGE_1M, "近一月")]:
        print(f"\n测试时间范围: {label}")
        try:
            df = get_survey_data(dc, range_type=range_type, page_size=20)
            print(f"✓ 获取成功: {len(df)} 行")
            print(f"  列名: {list(df.columns)[:10]}...")
            
            if len(df) > 0:
                if 'SUM' in df.columns:
                    max_sum = df.iloc[0]['SUM'] if len(df) > 0 else None
                    print(f"  SUM最大值（应该排在第一）: {max_sum}")
                    print(f"  前3行SUM值: {df.head(3)['SUM'].tolist()}")
                
                print(f"  前2行预览:")
                print(df.head(2)[['SECURITY_CODE', 'SECURITY_NAME_ABBR', 'SUM']].to_string())
        except Exception as e:
            print(f"✗ 失败: {e}")
            import traceback
            traceback.print_exc()


def test_t2():
    """测试表二：机构席位追踪 TopK交集"""
    print_section("测试表二：机构席位追踪 TopK交集")
    
    dc = EastMoneyDataCenter()
    
    for cycle, label in [(CYCLE_1M, "近一月"), (CYCLE_3M, "近三月"), (CYCLE_6M, "近六月")]:
        print(f"\n测试周期: {label}")
        try:
            top10_netbuy, top10_buycnt, inter = get_seat_topk_intersection(
                dc, cycle=cycle, k=10, page_size=50
            )
            print(f"✓ 获取成功")
            print(f"  Top10 by 净买额: {len(top10_netbuy)} 行")
            print(f"  Top10 by 买入次数: {len(top10_buycnt)} 行")
            print(f"  交集结果: {len(inter)} 行")
            
            if len(inter) > 0:
                codes = inter['SECURITY_CODE'].tolist()
                print(f"  交集股票代码: {codes[:10]}{'...' if len(codes) > 10 else ''}")
        except Exception as e:
            print(f"✗ 失败: {e}")
            import traceback
            traceback.print_exc()


def test_t3():
    """测试表三：机构买卖每日统计（多窗口去重合并）"""
    print_section("测试表三：机构买卖每日统计（多窗口去重合并）")
    
    dc = EastMoneyDataCenter()
    
    try:
        df = get_trade_netbuy_ratio_filtered(
            dc, ratio_col="RATIO", threshold=10.0, page_size=50
        )
        print(f"✓ 获取成功")
        print(f"  去重后行数: {len(df)}")
        
        if len(df) > 0:
            print(f"  列名: {list(df.columns)[:10]}...")
            print(f"\n前3行预览:")
            print(df.head(3)[['SECURITY_CODE', 'SECURITY_NAME_ABBR', 'RATIO', 'NET_BUY_AMT']].to_string())
            
            # 验证所有RATIO都 > 10.0
            if 'RATIO' in df.columns:
                import pandas as pd
                ratios = pd.to_numeric(df['RATIO'], errors='coerce')
                min_ratio = ratios.min()
                print(f"\n  验证: 最小RATIO值 = {min_ratio} (应该 > 10.0)")
                if min_ratio <= 10.0:
                    print(f"  ⚠ 警告: 存在RATIO <= 10.0的数据")
        else:
            print("  ⚠ 没有数据满足条件")
    except Exception as e:
        print(f"✗ 失败: {e}")
        import traceback
        traceback.print_exc()


def test_t4():
    """测试表四：表三 ∩ 表二"""
    print_section("测试表四：表三 ∩ 表二")
    
    dc = EastMoneyDataCenter()
    
    for cycle, label in [(CYCLE_1M, "近一月"), (CYCLE_3M, "近三月"), (CYCLE_6M, "近六月")]:
        print(f"\n测试周期: {label}")
        try:
            df = get_trade_x_seat_intersection(
                dc, cycle=cycle, page_size=50
            )
            print(f"✓ 获取成功")
            print(f"  交集行数: {len(df)}")
            
            if len(df) > 0:
                print(f"  列名: {list(df.columns)[:10]}...")
                codes = df['SECURITY_CODE'].tolist()
                print(f"  交集股票代码: {codes[:10]}{'...' if len(codes) > 10 else ''}")
                
                print(f"\n前2行预览:")
                display_cols = ['SECURITY_CODE', 'SECURITY_NAME_ABBR']
                if 'RATIO' in df.columns:
                    display_cols.append('RATIO')
                if 'NET_BUY_AMT' in df.columns:
                    display_cols.append('NET_BUY_AMT')
                print(df.head(2)[display_cols].to_string())
        except Exception as e:
            print(f"✗ 失败: {e}")
            import traceback
            traceback.print_exc()


def main():
    print("="*60)
    print("  测试所有表的实现函数")
    print("="*60)
    
    test_t1()
    test_t2()
    test_t3()
    test_t4()
    
    print_section("所有测试完成")
    print("请检查上述输出，确认所有实现函数工作正常")


if __name__ == "__main__":
    main()

