-- 创建时数据库 demo
CREATE DATABASE IF NOT EXISTS `demo`  DEFAULT CHARACTER SET utf8mb4  COLLATE utf8mb4_unicode_ci;

-- 创建订单表
DROP TABLE IF EXISTS `demo`.`order`;
CREATE TABLE IF NOT EXISTS `demo`.`order` (
    `symbol`         varchar(50)                 not null comment '股票代码',
    `date`           date                        not null comment '交易日期',
    `action`         varchar(20) default 'in'    not null comment '交易动作（in买入/out卖出）',
    `price`          varchar(100)                not null comment '成交价格',
    `size`           varchar(100)                not null comment '成交数量',
    `total_cost`     varchar(100)                not null comment '总成本',
    `remaining_cash` varchar(100)                not null comment '剩余资金',
    `create_time`    datetime    default (now()) null comment '创建日期'
) comment '订单日志';

-- 创建订单表
DROP TABLE IF EXISTS `demo`.`test_result`;
CREATE TABLE IF NOT EXISTS `demo`.`test_result` (
    `date`                date                         not null comment '交易日期',
    `hsi_rsi`             varchar(100)                 not null comment '恒生指数 相对强弱指数',
    `spx_rsi`             varchar(100)                 not null comment '标普500指数 相对强弱指数',
    `vix`                 varchar(100)                 not null comment '波动率 恐慌指数',
    `volatility_limiter`  varchar(100)                 not null comment '波动率限制',
    `sentiment_scores`    varchar(100)                 not null comment 'AI情绪得分',
    `news_weight`         varchar(100)                 not null comment 'AI新闻权重',
    `max_hedge_ratio`     varchar(100)                 not null comment '对冲比例',
    `rebalance_window`    varchar(100)                 not null comment '对冲窗口',
    `commission`          varchar(100)                 not null comment '交易佣金率',
    `slippage`            varchar(100)                 not null comment '滑点成本',
    `day_stop_loss`       varchar(100)                 not null comment '最大持仓天数',
    `remaining_cash`      varchar(100)                 not null comment '剩余资金',
    `create_time`         datetime    default (now())  null     comment '创建日期'
) comment '回测日志';


