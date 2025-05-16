# -*- coding: utf-8 -*-
from datetime import datetime

from dbutils import DBUtil, PageResult
from utils import BacktestPrinter
from order_info import OrderInfo

class OrderManager:
    """订单管理 保存、查询"""

    db_util = DBUtil()

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
        print(sql)
        OrderManager.db_util.save(sql)

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
        return OrderManager.db_util.get_all(sql, page, page_size)