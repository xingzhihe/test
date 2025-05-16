import backtrader as bt
import pandas as pd
import akshare as ak
import numpy as np

from utils import BacktestPrinter
from order import OrderInfo, OrderManager
from test_result import TestResult, TestResultManager

class DualMovingAverageStrategy(bt.Strategy):
    """
    多资产动态配置策略
    
    该策略采用自适应资产配置方法，通过多维度风险监控和动态再平衡机制，
    在不同市场环境下实现风险收益的最优配置。主要特点包括：
    
    1. 分层资产配置：将资产分为核心成长、避险、红利和对冲四大类别
    2. 动态风险管理：基于技术指标、波动率和AI情绪等多维度指标
    3. 自适应调仓机制：根据市场环境动态调整各类资产权重
    4. 智能对冲策略：通过多重触发条件进行择时对冲
    """
    
    params = (
        # 一、资产配置权重参数
        ("core_allocation", 0.45),       # 核心成长股配置比例：专注高ROE科技龙头
        ("gold_allocation", 0.28),       # 避险资产配置比例：黄金/白银/大宗商品
        ("dividend_allocation", 0.15),   # 红利股配置比例：高股息低估值蓝筹
        
        # 二、风险控制参数
        ("max_hedge_ratio", 0.3),        # 最大对冲比例：极端行情下的风险缓冲
        ("rebalance_window", 15),        # 再平衡周期：降低交易频率和成本
        ("ai_news_weight", 0.7),         # AI情绪因子权重：提升风险预警能力
        ("volatility_limiter", 0.025),   # 波动率阈值：用于止损和调仓决策
        ("time_stop_loss", 5),           # 最大持仓天数：控制单笔交易风险
        
        # 三、交易成本参数
        ("commission", 0.001),           # 交易佣金率：双向收取
        ("slippage", 0.005)             # 滑点成本：反映市场冲击成本
    )

    # 资产类别配置表：构建分散化的多资产组合
    asset_categories_config = {
        # 核心成长股：专注全球科技龙头，选择具有高ROE、强劲增长和护城河的优质标的
        "core": [
            "00700.HK",  # 腾讯：亚洲科技龙头，游戏+社交+支付全产业布局
            "AAPL.US",   # 苹果：硬件+服务双轮驱动，品牌溢价能力强
            "NVDA.US",   # 英伟达：AI芯片霸主，算力革命引领者
            "MSFT.US"    # 微软：云计算+AI巨头，企业级服务护城河深
        ],
        
        # 避险资产：通过贵金属和大宗商品对冲通胀和地缘风险
        "safe_haven": [
            "GLD.US",    # 黄金ETF：传统避险首选，对冲货币贬值
            "SLV.US",    # 白银ETF：工业属性+贵金属属性双重受益
            "USO.US",    # 原油ETF：对冲地缘政治风险和通胀压力
            "COPX.US"    # 铜矿ETF：受益于新能源和基建需求
        ],
        
        # 红利股：聚焦高股息低估值的优质蓝筹，提供稳定现金流
        "dividend": [
            "00939.HK",  # 建设银行：高股息率央企，估值优势明显
            "JPM.US",    # 摩根大通：全球顶级银行，分红稳定增长
            "BRK.B.US"   # 伯克希尔：价值投资典范，多元化业务布局
        ],
        
        # 对冲工具：用于市场剧烈波动时的风险对冲
        "hedge": [
            "SQQQ.US",   # 纳指三倍做空ETF：科技股大跌时的避险工具
            "07552.HK",  # 恒指波动期权：对冲港股市场系统性风险
            "SPY.US",    # 标普500ETF：用于观察美股整体走势
            "HSI.HK"     # 恒生指数：用于跟踪港股市场表现
        ]
    }

    def __init__(self):

        self.asset_categories = self.asset_categories_config # 实例中也保留一份，方便访问
        
        self._setup_technical_indicators()
        self._load_ai_sentiment_model()  # 模拟AI情绪模型（实盘接入NLPAPI）
        self.initialized = False  # 添加建仓标志位
        self.trades = []
        self.all_trades = []  # 用于记录所有交易

    def _setup_technical_indicators(self):
        """
        设置多维度市场监控指标
        
        构建多层次的技术指标体系，用于市场趋势判断和风险监控：
        1. RSI指标：分别监控港股和美股市场的超买超卖状态
        2. VIX波动率：跟踪市场恐慌情绪和系统性风险
        3. 个股波动率：计算各资产的波动率，用于动态调仓
        """
        # 恒生指数RSI：识别港股市场超买超卖
        self.hsi_rsi = bt.indicators.RSI(self.getdatabyname("HSI.HK"), period=14)
        # 标普500RSI：识别美股市场超买超卖
        self.spx_rsi = bt.indicators.RSI(self.getdatabyname("SPY.US"), period=14)
        # VIX波动率指数：市场恐慌情绪指标
        self.vix = self.getdatabyname("VXX.US").close
        # 计算所有资产的20日波动率：用于风险评估
        self.asset_vol = {d._name: bt.indicators.StandardDeviation(d, period=20) for d in self.datas}

    def _load_ai_sentiment_model(self):
        """
        加载AI新闻情绪模型
        
        通过AI分析新闻情绪，为交易决策提供额外维度：
        1. 使用Beta分布模拟情绪分数，范围0-1
        2. 参数调整反映不同资产的情绪偏向
        3. 实盘中可对接专业数据供应商API
        
        情绪分数说明：
        - 0.0-0.3：极度悲观
        - 0.3-0.4：悲观
        - 0.4-0.6：中性
        - 0.6-0.7：乐观
        - 0.7-1.0：极度乐观
        """
        self.sentiment_scores = {
            "0700.HK": np.random.beta(2, 1),    # 腾讯：设置偏乐观情绪分布
            "AAPL.US": np.random.beta(1.5, 1.2),  # 苹果：设置中性偏乐观分布
        }
        
    def next(self):
        if not self.initialized:
            # 找到所有数据源中最早的可用日期
            earliest_date = None
            for data in self.datas:
                if len(data) > 0:  # 确保数据源有数据
                    current_date = data.datetime.datetime(0)
                    if earliest_date is None or current_date < earliest_date:
                        earliest_date = current_date
            
            if earliest_date is None:
                return  # 如果没有可用数据，直接返回
            
            # 打印初始建仓时间点
            print(f"\n开始初始建仓，当前日期是: {earliest_date.strftime('%Y-%m-%d')}")

            # 初始建仓
            print("\n开始初始建仓...")
            BacktestPrinter.print_order_header()
            
            # 保存初始资金总额作为配置基准
            initial_total_value = self.broker.get_cash()
            total_value = initial_total_value
            
            # 按资产类别进行建仓
            for category, symbols in self.asset_categories.items():
                if category == "hedge":
                    continue  # 跳过对冲类资产的初始建仓
                    
                # 根据资产类别分配资金比例
                if category == "core":
                    allocation = self.p.core_allocation
                elif category == "safe_haven":
                    allocation = self.p.gold_allocation
                elif category == "dividend":
                    allocation = self.p.dividend_allocation
                else:
                    continue
                
                # 计算该类别的总投资金额
                category_value = initial_total_value * allocation
                per_asset_value = category_value / len(symbols)
                BacktestPrinter.print_allocation_info(
                    category=category,
                    total_value=category_value,
                    per_asset_value=per_asset_value
                )
                # 对该类别中的每个资产进行建仓
                for symbol in symbols:
                    try:
                        data = self.getdatabyname(symbol)
                        price = data.close[0]
                        if price > 0:
                            size = int(per_asset_value / price)
                            if size > 0:
                                # 计算交易成本
                                commission_cost = size * data.close[0] * self.p.commission
                                slippage_cost = size * data.close[0] * self.p.slippage
                                total_cost = commission_cost + slippage_cost
                                # 扣除成本后执行交易
                                order = self.buy(data=data, size=size)
                            if order:
                                self.broker.add_cash(-total_cost)
                                if order:
                                    # 记录交易信息
                                    trade_info = {
                                        'symbol': symbol,
                                        'datetime': earliest_date,
                                        'action': '买入',
                                        'price': price,
                                        'size': size,
                                        'value': price * size,
                                        'pnl': 0  # 初始盈亏为0
                                    }
                                    self.trades.append(trade_info)
                                    self.all_trades.append(trade_info)
                                        
                                    # 更新剩余资金
                                    total_value -= (price * size)
                                        
                                    # 打印交易信息
                                    # BacktestPrinter.print_order_info(
                                    OrderManager.save(OrderInfo(
                                        symbol=symbol,
                                        date=earliest_date,
                                        action="买入",
                                        price=price,
                                        size=size,
                                        total_cost=price * size,
                                        remaining_cash=total_value
                                    ))
                        else:
                            print(f"跳过{symbol}：未满足金叉条件")
                    except Exception as e:
                        print(f"建仓{symbol}时发生错误: {e}")
                        continue
            
            print("\n初始建仓完成")
            self.initialized = True
            
        else:
            print(f"当前回测日期: {self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d')}")
            # 每日动态调整逻辑
            self._dynamic_rebalance()
            self._adaptive_hedging()
            self._enforce_risk_controls()

    def _dynamic_rebalance(self):
        """
        基于波动率的动态再平衡机制
        
        核心功能：
        1. 实时监控各类资产的配置偏离度
        2. 当偏离度超过阈值时触发再平衡
        3. 考虑交易成本和市场冲击
        
        主要步骤：
        1. 计算当前各类资产实际权重
        2. 对比目标配置比例计算偏离度
        3. 偏离超过8%时触发再平衡
        4. 排除对冲资产，仅平衡核心资产
        """
        # 获取当前资产配置比例
        current_allocation = self._calculate_current_allocation()
        
        # 设定各类资产的目标配置比例
        target_allocations = {
            "core": self.p.core_allocation,         # 核心成长股目标仓位
            "safe_haven": self.p.gold_allocation,  # 避险资产目标仓位
            "dividend": self.p.dividend_allocation  # 红利股目标仓位
            # 对冲资产不参与常规再平衡，而是通过市场信号动态调整
        }
        
        # 遍历检查各资产类别是否需要再平衡
        for cat_name, target in target_allocations.items():
            if cat_name in current_allocation:  # 确保资产类别存在
                # 当配置偏离超过8%时触发再平衡
                if abs(current_allocation[cat_name] - target) > 0.08:
                    self._rebalance_category(cat_name, target)

    def _adaptive_hedging(self):
        """
        AI增强型对冲决策系统
        
        核心功能：
        1. 多维度市场风险监控
        2. 智能对冲仓位管理
        3. 动态调整对冲比例
        
        触发条件（需同时满足）：
        1. 技术指标：RSI超卖（<30）
        2. 波动率指标：VIX高位（>25）
        3. 情绪指标：AI情绪得分低位（<0.4）
        
        对冲策略：
        - 触发时按最大对冲比例开仓
        - 使用反向ETF和期权组合对冲
        - 对冲金额根据总资产动态调整
        """
        # 检查三重触发条件
        # print(f"回测日期:{self.datas[0].datetime.datetime(0).strftime('%Y-%m-%d')}; HSI.RSI:{self.hsi_rsi[0]}; SPX.RSI:{self.spx_rsi[0]}; VIX:{self.vix[0]}; AI情绪得分:{np.mean(list(self.sentiment_scores.values()))}; 资金余额:{self.broker.getvalue()}; 对冲比例:{self.p.max_hedge_ratio}; 对冲窗口:{self.p.rebalance_window}; AI情绪权重:{self.p.ai_news_weight}; 波动率限制:{self.p.volatility_limiter}; 最大持仓天数:{self.p.time_stop_loss}; 交易佣金率:{self.p.commission}; 滑点成本:{self.p.slippage}")
        TestResultManager.save(TestResult(self.datas[0].datetime.datetime(0), self.hsi_rsi[0], self.spx_rsi[0], np.mean(list(self.sentiment_scores.values())), self.p.ai_news_weight, self.p.max_hedge_ratio, self.p.rebalance_window, self.p.volatility_limiter, self.vix[0], self.p.commission, self.p.slippage, self.p.time_stop_loss, self.broker.getvalue()))
        if (self.hsi_rsi < 30 or self.spx_rsi < 30) and \
            self.vix[0] > 25 and \
            np.mean(list(self.sentiment_scores.values())) < 0.4:  # 负面情绪主导
            # 计算对冲金额并执行对冲
            hedge_amount = self.broker.getvalue() * self.p.max_hedge_ratio
            self._distribute_hedge_etf(hedge_amount)
        else:
            print("未触发对冲条件")

    def _enforce_risk_controls(self):
        """
        多维度风险控制系统
        
        核心功能：
        1. 波动率监控和止损
        2. 仓位上限控制
        3. 资金利用率优化
        
        主要风控措施：
        1. 波动率止损：
            - 计算20日收盘价的Z-score
            - Z-score < -1.5时触发止损
            - 每次减仓30%控制冲击
        
        2. 单一持仓限制：
            - 单一标的最大仓位8%
            - 超限时自动减仓20%
            - 控制个股黑天鹅风险
        """
        # 遍历所有持仓进行风控检查
        for data_name, pos in self.getpositions().items():
            if pos.size == 0:  # 跳过空仓位
                continue
            # 获取数据对象的股票代码
            data = self.getdatabyname(data_name._name if hasattr(data_name, '_name') else data_name)
            
            # 1. 波动率止损检查
            if len(data.close) >= 20:
                # 计算最近20日收盘价的Z-score
                close_prices = np.array([data.close[i] for i in range(-20, 0)])
                z_score = (close_prices - np.mean(close_prices)) / np.std(close_prices)
                
                # Z-score过低表明价格异常下跌，触发止损
                if z_score[-1] < -1.5:
                    reduce_size = int(pos.size * 0.3)  # 减仓30%
                    if reduce_size > 0:
                        order = self.sell(data=data, size=reduce_size)
                        if order:
                            # 计算交易成本
                            commission_cost = reduce_size * data.close[0] * self.p.commission
                            slippage_cost = reduce_size * data.close[0] * self.p.slippage
                            total_cost = commission_cost + slippage_cost
                            # 扣除成本
                            self.broker.add_cash(-total_cost)
                            # 记录交易信息
                            trade_info = {
                                'datetime': self.datas[0].datetime.datetime(0),
                                'action': '卖出',
                                'price': data.close[0],
                                'size': reduce_size,
                                'value': data.close[0] * reduce_size
                            }
                            self.trades.append(trade_info)
                            # 打印交易信息
                            # print("{:<8} {:<12} {:<6} {:<10.2f} {:<8d} {:<12.2f} {:<14.2f}".format(
                            #     data_name._name if hasattr(data_name, '_name') else data_name,
                            #     self.datas[0].datetime.datetime(0).strftime("%Y-%m-%d"),
                            #     "卖出",
                            #     data.close[0],
                            #     reduce_size,
                            #     data.close[0] * reduce_size,
                            #     self.broker.get_cash()
                            # ))
                            OrderManager.save(OrderInfo(
                                symbol=data_name._name if hasattr(data_name, '_name') else data_name,
                                date=self.datas[0].datetime.datetime(0),
                                action="卖出",
                                price=data.close[0],
                                size=reduce_size,
                                total_cost=data.close[0] * reduce_size,
                                remaining_cash=self.broker.get_cash()
                            ))
            
            # 2. 单一标的持仓上限控制
            position_value = pos.size * data.close[0]
            if position_value / self.broker.getvalue() > 0.08:  # 超过8%上限
                reduce_size = int(pos.size * 0.2)  # 减仓20%
                if reduce_size > 0:
                    order = self.sell(data=data, size=reduce_size)
                    if order:
                        # 计算交易成本
                        commission_cost = reduce_size * data.close[0] * self.p.commission
                        slippage_cost = reduce_size * data.close[0] * self.p.slippage
                        total_cost = commission_cost + slippage_cost
                        # 扣除成本
                        self.broker.add_cash(-total_cost)
                        # 记录交易信息
                        trade_info = {
                            'datetime': self.datas[0].datetime.datetime(0),
                            'action': '卖出',
                            'price': data.close[0],
                            'size': reduce_size,
                            'value': data.close[0] * reduce_size
                        }
                        self.trades.append(trade_info)
                        # 打印交易信息
                        # print("{:<8} {:<12} {:<6} {:<10.2f} {:<8d} {:<12.2f} {:<14.2f}".format(
                        #     data_name._name if hasattr(data_name, '_name') else data_name,
                        #     self.datas[0].datetime.datetime(0).strftime("%Y-%m-%d"),
                        #     "卖出",
                        #     data.close[0],
                        #     reduce_size,
                        #     data.close[0] * reduce_size,
                        #     self.broker.get_cash()
                        # ))
                        OrderManager.save(OrderInfo(
                            symbol=data_name._name if hasattr(data_name, '_name') else data_name,
                            date=self.datas[0].datetime.datetime(0),
                            action="卖出",
                            price=data.close[0],
                            size=reduce_size,
                            total_cost=data.close[0] * reduce_size,
                            remaining_cash=self.broker.get_cash()
                        ))

    def _calculate_current_allocation(self):
        """实时资产配置计算"""
        total_value = self.broker.getvalue()
        allocations = {}
        
        for category, symbols in self.asset_categories.items():
            category_value = 0
            for symbol in symbols:
                try:
                    data = self.getdatabyname(symbol)
                    pos = self.getposition(data)
                    if pos and pos.size > 0:
                        category_value += pos.size * data.close[0]
                except Exception:
                    continue
            allocations[category] = category_value / total_value if total_value > 0 else 0
            
        return allocations

    def _rebalance_category(self, category_name, target_allocation):
        """执行单个类别的再平衡操作"""
        current_value = self.broker.getvalue()
        target_value = current_value * target_allocation
        
        # 获取当前类别的实际价值
        current_category_value = 0
        for symbol in self.asset_categories[category_name]:
            try:
                data = self.getdatabyname(symbol)
                pos = self.getposition(data)
                if pos and pos.size > 0:
                    current_category_value += pos.size * data.close[0]
            except Exception:
                continue
        
        # 计算需要调整的金额
        value_difference = target_value - current_category_value
        if abs(value_difference) > current_value * 0.02:  # 设置2%的最小调整阈值
            # 获取类别中的所有可交易资产
            tradeable_assets = []
            for symbol in self.asset_categories[category_name]:
                try:
                    data = self.getdatabyname(symbol)
                    if data and data.close[0] > 0:
                        tradeable_assets.append((symbol, data))
                except Exception:
                    continue
            
            if tradeable_assets:
                # 平均分配调整金额
                value_per_asset = value_difference / len(tradeable_assets)
                
                for symbol, data in tradeable_assets:
                    try:
                        price = data.close[0]
                        size_change = int(value_per_asset / price)
                        
                        if size_change > 0:
                            order = self.buy(data=data, size=size_change)
                            if order:
                                # 打印交易信息
                                #print("{:<8} {:<12} {:<6} {:<10.2f} {:<8d} {:<12.2f} {:<14.2f}".format(symbol, self.datas[0].datetime.datetime(0).strftime("%Y-%m-%d"), "买入", data.close[0], size_change, data.close[0] * size_change, self.broker.get_cash()))
                                OrderManager.save(OrderInfo(
                                        symbol=symbol,
                                        date=self.datas[0].datetime.datetime(0),
                                        action="买入",
                                        price=data.close[0],
                                        size=size_change,
                                        total_cost=data.close[0] * size_change,
                                        remaining_cash=self.broker.get_cash()
                                    ))
                        elif size_change < 0:
                            # 计算交易成本
                            commission_cost = abs(size_change) * data.close[0] * self.p.commission
                            slippage_cost = abs(size_change) * data.close[0] * self.p.slippage
                            total_cost = commission_cost + slippage_cost
                            # 扣除成本后执行交易
                            order = self.sell(data=data, size=abs(size_change))
                            if order:
                                self.broker.add_cash(-total_cost)
                            if order:
                                # print("{:<8} {:<12} {:<6} {:<10.2f} {:<8d} {:<12.2f} {:<14.2f}".format(symbol, self.datas[0].datetime.datetime(0).strftime("%Y-%m-%d"), "卖出", data.close[0], abs(size_change), data.close[0] * abs(size_change), self.broker.get_cash()))
                                # 打印交易信息
                                OOrderManager.save(OrderInfo(
                                    symbol=symbol,
                                    date=self.datas[0].datetime.datetime(0),
                                    action="卖出",
                                    price=data.close[0],
                                    size=abs(size_change),
                                    total_cost=data.close[0] * abs(size_change),
                                    remaining_cash=self.broker.get_cash()
                                ))
                    except Exception as e:
                        print(f"再平衡{symbol}时发生错误: {e}")
                        continue

    def _distribute_hedge_etf(self, hedge_amount):
        """分配对冲资金到对冲类ETF"""
        hedge_symbols = self.asset_categories.get("hedge", [])
        if not hedge_symbols:
            return
            
        amount_per_etf = hedge_amount / len(hedge_symbols)
        for symbol in hedge_symbols:
            try:
                data = self.getdatabyname(symbol)
                if data is None:
                    continue
                    
                price = data.close[0]
                if price > 0:
                    size = int(amount_per_etf / price)
                    if size > 0:
                        # 计算交易成本
                        commission_cost = size * data.close[0] * self.p.commission
                        slippage_cost = size * data.close[0] * self.p.slippage
                        total_cost = commission_cost + slippage_cost
                        # 扣除成本后执行交易
                        order = self.buy(data=data, size=size)
                        if order:
                            self.broker.add_cash(-total_cost)
                        if order:
                            print(f"对冲买入: {symbol}, {size}股")
            except Exception as e:
                print(f"对冲{symbol}时发生错误: {e}")
                continue

def load_data(start="2021-01-08", end="2025-05-10"):
    """加载和处理所有资产的数据
    
    Args:
        start: 开始日期，格式为'YYYY-MM-DD'
        end: 结束日期，格式为'YYYY-MM-DD'
        
    Returns:
        dict: 包含所有加载成功的数据，key为资产代码，value为backtrader的Data Feed对象
    """
    # 获取所有需要的资产代码
    symbols = []
    for category, assets in DualMovingAverageStrategy.asset_categories_config.items():
        symbols.extend(assets)
    symbols.extend(['VXX.US'])  # 添加额外需要的指数
    
    data_feeds = {}
    
    # 下载并处理每个资产的数据
    for symbol in symbols:
        try:
            if '.HK' in symbol:
                # 处理港股数据
                try:
                    # 获取港股历史数据，使用stock_hk_daily替代stock_hk_hist_min_em
                    stock_code = symbol.replace('.HK', '')
                    
                    stock_data = ak.stock_hk_daily(symbol=stock_code, adjust="qfq")
                    if stock_data is None or stock_data.empty:
                        print(f"未能获取到 {symbol} 的历史数据")
                        continue
                        
                    stock_data.rename(columns={
                        'date': 'datetime',
                        'open': 'Open',
                        'high': 'High',
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume'
                    }, inplace=True)
                except Exception as e:
                    print(f"获取港股 {symbol} 数据时出错: {str(e)}")
                    continue
            elif '.US' in symbol:
                # 处理美股数据
                stock_data = ak.stock_us_daily(symbol=symbol.replace('.US', ''), adjust='qfq')
                stock_data.rename(columns={
                    'date': 'datetime',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                }, inplace=True)
            
            # 统一处理时间格式
            stock_data['datetime'] = pd.to_datetime(stock_data['datetime'])
            stock_data.set_index('datetime', inplace=True)
            
            # 过滤日期范围
            stock_data = stock_data.loc[start:end]
            
            if not stock_data.empty:
                # 计算数据统计信息
                data_count = len(stock_data)
                earliest_date = stock_data.index.min().strftime('%Y-%m-%d')
                latest_date = stock_data.index.max().strftime('%Y-%m-%d')
                
                data = bt.feeds.PandasData(dataname=stock_data)
                data_feeds[symbol] = data
                print(f'数据加载成功 {symbol}: 数据条数: {data_count}, 最早日期: {earliest_date}, 最后日期: {latest_date}')
            else:
                print(f'{symbol} 未能加载到数据 ')
                
        except Exception as e:
            print(f'Error downloading data for {symbol}: {e}')
            continue
    
    return data_feeds

def run_backtest(start="2019-05-10", end="2025-05-10", initial_cash=15000000):
    cerebro = bt.Cerebro()
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    
    # 加载数据
    data_feeds = load_data(start, end)
    
    # 将数据添加到cerebro
    for symbol, data in data_feeds.items():
        cerebro.adddata(data, name=symbol)
    
    cerebro.addstrategy(DualMovingAverageStrategy)
    cerebro.broker.setcash(initial_cash)
    
    print('初始投资组合价值: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    strat = results[0]
    
    # 获取最终投资组合价值
    final_portfolio_value = cerebro.broker.getvalue()
    print('最终投资组合价值: %.2f' % final_portfolio_value)
    
    # 计算总收益率
    total_return = (final_portfolio_value - initial_cash) / initial_cash * 100
    print('\n策略收益分析：')
    print('总收益率: %.2f%%' % total_return)
    
    # 获取夏普比率
    sharpe_ratio = strat.analyzers.sharpe_ratio.get_analysis()['sharperatio']
    print('夏普比率: %.2f' % sharpe_ratio if sharpe_ratio else '夏普比率: N/A')
    
    # 获取最大回撤
    drawdown = strat.analyzers.drawdown.get_analysis()
    max_drawdown = drawdown.max.drawdown
    print('最大回撤: %.2f%%' % max_drawdown if max_drawdown else '最大回撤: N/A')
    
    # 获取年化收益率
    returns = strat.analyzers.returns.get_analysis()
    rnorm100 = returns.get('rnorm100', 0.0)
    print('年化收益率: %.2f%%' % (rnorm100 * 100) if rnorm100 else '年化收益率: N/A')
    
    # 获取交易分析
    trade_analysis = strat.analyzers.trade_analyzer.get_analysis()
    
    # 打印交易统计
    print('\n交易统计：')
    total_trades = trade_analysis['total']['total'] if 'total' in trade_analysis and 'total' in trade_analysis['total'] else 0
    won_trades = trade_analysis['won']['total'] if 'won' in trade_analysis and 'total' in trade_analysis['won'] else 0
    lost_trades = trade_analysis['lost']['total'] if 'lost' in trade_analysis and 'total' in trade_analysis['lost'] else 0
    print(f'总交易次数: {total_trades}')
    print(f'盈利交易: {won_trades}')
    print(f'亏损交易: {lost_trades}')
    
    # 打印交易明细
    # print('\n交易明细：')
    # for trade in strat.trades:
    #    print(f"{trade['datetime']} | {trade['action'].upper()} | 价格: {trade['price']:.2f} | 数量: {trade['size']:.2f} | 总金额: {trade['value']:.2f}")


if __name__ == '__main__':
    run_backtest()