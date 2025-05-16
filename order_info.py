# -*- coding: utf-8 -*-
from datetime import datetime

class OrderInfo:
    """订单信息模型"""

    def __init__(self, symbol: str, date: datetime, action: str, 
                 price: float, size: int, total_cost: float, remaining_cash: float):
        # 股票代码
        self.symbol = symbol

        # 交易日期
        self.date = date
        
        # 交易类型：in 买入；out 卖出
        self.action = action
        
        # 成交价格
        self.price = price
        
        # 成交数量
        self.size = size
        
        # 总成本
        self.total_cost = total_cost
        
        # 剩余现金
        self.remaining_cash = remaining_cash

