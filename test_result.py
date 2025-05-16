# -*- coding: utf-8 -*-
from datetime import datetime

from dbutils import DBUtil, PageResult

class TestResult:
    """回测日志模型"""

    def __init__(self, date: datetime, hsi_rsi: float, spx_rsi: float, 
                 sentiment_scores: float, news_weight: float, 
                 max_hedge_ratio: float, rebalance_window: int, 
                 volatility_limiter: float, vix: float, 
                 commission: float, slippage: float, 
                 day_stop_loss: int, remaining_cash: float):
        # 回测日期
        self.date = date

        # 恒生 相对强弱指数
        self.hsi_rsi = hsi_rsi
        
        # 标普500 相对强弱指数
        self.spx_rsi = spx_rsi
        
        # AI情绪评分
        self.sentiment_scores = sentiment_scores
        
        # AI情绪权重
        self.news_weight = news_weight
        
        # 对冲比例
        self.max_hedge_ratio = max_hedge_ratio
        
        # 对冲窗口
        self.rebalance_window = rebalance_window
        
        # 波动率限制
        self.volatility_limiter = volatility_limiter
        
        # 波动率 恐慌指数
        self.vix = vix
        
        # 交易佣金率
        self.commission = commission
        
        # 滑点成本
        self.slippage = slippage
        
        # 最大持仓天数
        self.day_stop_loss = day_stop_loss
        
        # 剩余现金
        self.remaining_cash = remaining_cash


class TestResultManager:
    """回测结果管理 保存、查询"""

    @staticmethod
    def save(result: TestResult) -> None:
        """
        保存回测结果
        
        Args:
            result: 回测结果
        """
        print(f"回测日期:{result.date.strftime('%Y-%m-%d')}; \
HSI.RSI:{result.hsi_rsi}; \
SPX.RSI:{result.spx_rsi}; \
VIX:{result.vix}; \
AI情绪得分:{result.sentiment_scores}; \
资金余额:{result.remaining_cash}; \
对冲比例:{result.max_hedge_ratio}; \
对冲窗口:{result.rebalance_window}; \
AI情绪权重:{result.news_weight}; \
波动率限制:{result.volatility_limiter}; \
最大持仓天数:{result.day_stop_loss}; \
交易佣金率:{result.commission}; \
滑点成本:{result.slippage}")

        sql = f"INSERT INTO `test_result`(`date`, `hsi_rsi`, `spx_rsi`, `vix`, `volatility_limiter`, \
`sentiment_scores`, `news_weight`, `max_hedge_ratio`, `rebalance_window`, `commission`, `slippage`, `day_stop_loss`, `remaining_cash`) VALUES (\
'{result.date.strftime("%Y-%m-%d")}', \
'{result.hsi_rsi}', \
'{result.spx_rsi}', \
'{result.vix}', \
'{result.volatility_limiter}', \
'{result.sentiment_scores}', \
'{result.news_weight}', \
'{result.max_hedge_ratio}', \
'{result.rebalance_window}', \
'{result.commission}', \
'{result.slippage}', \
'{result.day_stop_loss}', \
'{result.remaining_cash:.2f}')"
        # print(sql)
        DBUtil.INS().save(sql)

    @staticmethod
    def list(page: int, page_size: int = 10) -> PageResult:
        """
        分页回测结果信息
        
        Args:
            page: 当前页码，从1开始
            page_size：每页显示数量，默认10条数据
        """

        offset = (page - 1) * page_size
        sql = f"SELECT `date`, `hsi_rsi`, `spx_rsi`, `vix`, `volatility_limiter`, `sentiment_scores`, `news_weight`, \
`max_hedge_ratio`, `rebalance_window`, `commission`, `slippage`, `day_stop_loss`, `remaining_cash` FROM `test_result`"
        return DBUtil.INS().get_all(sql, page, page_size)