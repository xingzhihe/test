# -*- coding: utf-8 -*-
from datetime import datetime

from dbutils import DBUtil
from utils import BacktestPrinter

class OrderManager:
    """订单管理 保存、查询"""

    db_util = DBUtil()

    @staticmethod
    def save(symbol: str, date: datetime, action: str, price: float, 
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
        BacktestPrinter.print_order_info(symbol, date, action, price, size, total_cost, remaining_cash)

        sql = f"INSERT INTO `order`(`symbol`, `date`, `action`, `price`, `size`, `total_cost`, `remaining_cash`) VALUES ('{symbol}', '{date.strftime("%Y-%m-%d")}', '{'in' if action=="买入" else 'out'}', '{price:.2f}', '{size}', '{total_cost:.2f}', '{remaining_cash:.2f}')"
        OrderManager.db_util.save(sql)