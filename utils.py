# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

from dbutils import DBUtil

class BacktestPrinter:
    """
    回测打印工具类
    
    提供统一的打印格式和方法，用于输出回测过程中的各类信息，包括：
    1. 订单信息打印
    2. 每日回测日志打印
    3. 资产配置信息打印
    4. 回测结果统计打印
    """
    db_util = DBUtil()

    @staticmethod
    def print_order_info(symbol: str, date: datetime, action: str, price: float, 
                        size: int, total_cost: float, remaining_cash: float) -> None:
        """
        打印订单信息
        
        Args:
            symbol: 股票代码
            date: 交易日期
            action: 交易动作（买入/卖出）
            price: 成交价格
            size: 成交数量
            total_cost: 总成本
            remaining_cash: 剩余资金
        """
        print("{:<8} {:<12} {:<6} {:<10.2f} {:<8d} {:<12.2f} {:<14.2f}".format(
            symbol,
            date.strftime("%Y-%m-%d"),
            action,
            price,
            size,
            total_cost,
            remaining_cash
        ))

        sql = f"INSERT INTO `order`(`symbol`, `date`, `action`, `price`, `size`, `total_cost`, `remaining_cash`) VALUES ('{symbol}', '{date.strftime("%Y-%m-%d")}', '{'in' if action=="买入" else 'out'}', '{price:.2f}', '{size}', '{total_cost:.2f}', '{remaining_cash:.2f}')"
        BacktestPrinter.db_util.save(sql)
    
    @staticmethod
    def print_order_header() -> None:
        """
        打印订单信息表头
        """
        print("{:<8} {:<12} {:<6} {:<10} {:<8} {:<12} {:<14}".format(
            "股票代码", "日期", "操作", "单价", "数量", "总金额", "剩余资金"
        ))
    
    @staticmethod
    def print_daily_stats(date: datetime, indicators: Dict[str, float], 
                         sentiment_scores: Dict[str, float], portfolio_value: float) -> None:
        """
        打印每日回测统计信息
        
        Args:
            date: 当前回测日期
            indicators: 技术指标数据
            sentiment_scores: AI情绪得分
            portfolio_value: 当前组合市值
        """
        print(f"\n当前回测日期: {date.strftime('%Y-%m-%d')}")
        print(f"当前HSI.RSI: {indicators.get('hsi_rsi', 'N/A')}")
        print(f"当前SPX.RSI: {indicators.get('spx_rsi', 'N/A')}")
        print(f"当前VIX: {indicators.get('vix', 'N/A')}")
        print(f"当前AI情绪得分: {sum(sentiment_scores.values()) / len(sentiment_scores) if sentiment_scores else 'N/A'}")
        print(f"当前资金余额: {portfolio_value:.2f}")
    
    @staticmethod
    def print_allocation_info(category: str, total_value: float, per_asset_value: float) -> None:
        """
        打印资产配置信息
        
        Args:
            category: 资产类别
            total_value: 该类别总投资金额
            per_asset_value: 每个资产的投资金额
        """
        print(f"\n{category}类别的总投资金额: {total_value:.2f}")
        print(f"每个{category}类别的投资金额: {per_asset_value:.2f}")
    
    @staticmethod
    def print_rebalance_info(category: str, current_allocation: float, 
                           target_allocation: float, deviation: float) -> None:
        """
        打印再平衡信息
        
        Args:
            category: 资产类别
            current_allocation: 当前配置比例
            target_allocation: 目标配置比例
            deviation: 偏离度
        """
        print(f"Rebalancing {category}: 当前配置={current_allocation:.2%}, "
              f"目标={target_allocation:.2%}, 偏离={deviation:.2%}")
    
    @staticmethod
    def print_backtest_results(initial_value: float, final_value: float, 
                             sharpe_ratio: float, max_drawdown: float,
                             annual_returns: Dict[int, float],
                             trade_analysis: Dict[str, Any],
                             all_trades: List[Dict[str, Any]] = None) -> None:
        """
        打印回测结果统计
        
        Args:
            initial_value: 初始资金
            final_value: 最终市值
            sharpe_ratio: 夏普比率
            max_drawdown: 最大回撤
            annual_returns: 年度收益率
            trade_analysis: 交易分析结果
            all_trades: 所有交易记录列表
        """
        print(f"\n回测结果统计")
        print(f"初始资金: {initial_value:.2f}")
        print(f"最终市值: {final_value:.2f}")
        print(f"夏普比率: {sharpe_ratio:.2f}" if sharpe_ratio is not None else "夏普比率: 无数据")
        print(f"最大回撤: {max_drawdown:.2%}" if max_drawdown is not None else "最大回撤: 无数据")
        
        print("\n年度收益率:")
        for year, ret in annual_returns.items():
            print(f"  {year}: {ret:.2%}" if ret is not None else f"  {year}: 无数据")
        
        print("\n交易分析:")
        
        # 优先使用完整的交易记录统计
        if all_trades is not None:
            total_trades = len(all_trades)
            won_trades = len([t for t in all_trades if t.get('pnl', 0) > 0])
            lost_trades = len([t for t in all_trades if t.get('pnl', 0) < 0])
            avg_win = np.mean([t['pnl'] for t in all_trades if t.get('pnl', 0) > 0]) if won_trades > 0 else None
            avg_loss = np.mean([t['pnl'] for t in all_trades if t.get('pnl', 0) < 0]) if lost_trades > 0 else None
        else:
            # 回退到trade_analysis的统计
            total_trades = trade_analysis.get('total', {}).get('total')
            won_trades = trade_analysis.get('won', {}).get('total')
            lost_trades = trade_analysis.get('lost', {}).get('total')
            avg_win = trade_analysis.get('won', {}).get('pnl', {}).get('average')
            avg_loss = trade_analysis.get('lost', {}).get('pnl', {}).get('average')
        
        print(f"  总交易次数: {total_trades if total_trades is not None else '无数据'}")
        print(f"  盈利交易: {won_trades if won_trades is not None else '无数据'}")
        print(f"  亏损交易: {lost_trades if lost_trades is not None else '无数据'}")
        print(f"  平均盈利: {avg_win:.2f}" if avg_win is not None else "  平均盈利: 无数据")
        print(f"  平均亏损: {avg_loss:.2f}" if avg_loss is not None else "  平均亏损: 无数据")
        
        # 打印前5笔交易示例
        if all_trades is not None and len(all_trades) > 0:
            print("\n交易记录示例:")
            for i, trade in enumerate(all_trades[:5]):
                print(f"  交易{i+1}: {trade.get('symbol', '未知')} {trade.get('action', '未知')} "
                      f"{trade.get('size', 0)}股 @{trade.get('price', 0):.2f}")