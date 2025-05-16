# -*- coding: utf-8 -*-
from datetime import datetime

from dbutils import DBUtil, PageResult
from utils import BacktestPrinter

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


class OrderManager:
    """订单管理 保存、查询"""

    @staticmethod
    def save(order: OrderInfo) -> None:
        """
        保存订单信息
        
        Args:
            order: 订单信息
        """
        BacktestPrinter.print_order_info(order.symbol, order.date, order.action, order.price, order.size, order.total_cost, order.remaining_cash)

        sql = f"INSERT INTO `order`(`symbol`, `date`, `action`, `price`, `size`, `total_cost`, `remaining_cash`) VALUES (\
'{order.symbol}', \
'{order.date.strftime("%Y-%m-%d")}', \
'{'in' if order.action=="买入" else 'out'}', \
'{order.price:.2f}', \
'{order.size}', \
'{order.total_cost:.2f}', \
'{order.remaining_cash:.2f}'\
)"
        DBUtil.INS().save(sql)

    @staticmethod
    def list(page: int, page_size: int = 10) -> PageResult:
        """
        分页订单信息
        
        Args:
            page: 当前页码，从1开始
            page_size：每页显示数量，默认10条数据
        """

        offset = (page - 1) * page_size
        sql = f"SELECT `symbol`, `date`, `action`, `price`, `size`, `total_cost`, `remaining_cash` FROM `order`"
        return DBUtil.INS().get_all(sql, page, page_size)