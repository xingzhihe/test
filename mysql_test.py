# -*- coding: utf-8 -*-
import json

from dbutils import DBUtil


if __name__ == '__main__':
    dbUtil = DBUtil()
    print("对象实例后的属性：" + json.dumps(dbUtil.__dict__))

    # 主键查询
    sql = "select * from `order` where symbol = 'HK'"
    print("get_one执行结果：" + str(dbUtil.get_one(sql)))

    # 列表查询
    sql = "select * from `order` order by create_time desc limit 1"
    print("get_all执行结果：" + str(dbUtil.get_all(sql)))

    # 插入
    sql = "INSERT INTO `order`(`symbol`, `date`, `action`, `price`, `size`, `total_cost`, `remaining_cash`) "
    sql = sql + "VALUES ('HK', '2025-05-15', 'in', '1688.5675', '94533434', '3545657567', '867967.258')"
    print("save执行结果：" + str(dbUtil.save(sql)))

    # 列表查询
    sql = "select * from `order` order by create_time desc limit 1"
    print("get_all执行结果：" + str(dbUtil.get_all(sql)))

    # 更新
    sql = "update `order` set price= '4354.6768' where symbol = 'HK'"
    print("update执行结果：" + str(dbUtil.update(sql)))

    # 列表查询
    sql = "select * from `order` order by create_time desc limit 1"
    print("get_all执行结果：" + str(dbUtil.get_all(sql)))

    # 删除
    sql = "delete from `order` where symbol = 'HK'"
    print("delete执行结果：" + str(dbUtil.delete(sql)))

    # 列表查询
    sql = "select * from `order` order by create_time desc limit 1"
    print("get_all执行结果：" + str(dbUtil.get_all(sql)))
