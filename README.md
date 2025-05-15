# test
test for code-server

进入code-server后
1. 安装 汉化 插件，切换语言
2. 安装python插件
3. 安装github插件
4. 克隆github仓库代码并在新窗口打开
5. 创建python虚拟环境
6. 进入python虚拟环境，安装依赖包模块
7. 运行python代码

mysql依赖模块：
1. pip3 install pymysql
2. pip3 install cryptography



select  user, host from mysql.user;
create user 'test'@'%' identified by 'test';
grant all privileges on *.* to 'test'@'%' with grant option;
flush privileges;

CREATE DATABASE IF NOT EXISTS `demo`  DEFAULT CHARACTER SET utf8mb4  COLLATE utf8mb4_unicode_ci;

DROP TABLE IF EXISTS demo.`order`;
CREATE TABLE IF NOT EXISTS demo.`order`
(
    symbol         varchar(50)                 not null comment '股票代码',
    date           date                        not null comment '交易日期',
    action         varchar(20) default 'in'    not null comment '交易动作（in买入/out卖出）',
    price          varchar(100)                not null comment '成交价格',
    size           varchar(100)                not null comment '成交数量',
    total_cost     varchar(100)                not null comment '总成本',
    remaining_cash varchar(100)                not null comment '剩余资金',
    create_time    datetime    default (now()) null comment '创建日期'
) comment '订单日志';

INSERT INTO `order`(`symbol`, `date`, `action`, `price`, `size`, `total_cost`, `remaining_cash`) 
VALUES ('HK', '2025-05-15', 'in', '1688.5675', '94533434', '3545657567', '867967.258');

select * from demo.`order` where symbol = 'HK';