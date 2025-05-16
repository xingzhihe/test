# -*- coding: utf-8 -*-
import json

from order_manager import OrderManager


if __name__ == '__main__':
    dbUtil = OrderManager.db_util
    print("对象实例后的属性：" + json.dumps(dbUtil.__dict__))

    # 列表查询
    page = 1
    page_size = 50
    pageResult = OrderManager.list(page, page_size)
    print(f"get_all执行结果：{pageResult.page}/{pageResult.pages} 每页显示{pageResult.page_size}条，总记录数{pageResult.records}条")
    for iter in pageResult.data:
        print(f"\t{iter}")
    
    while(not pageResult.eop):
        page = page + 1
        pageResult = OrderManager.list(page, page_size)
        print(f"get_all执行结果：{pageResult.page}/{pageResult.pages} 每页显示{pageResult.page_size}条，总记录数{pageResult.records}条")
        for iter in pageResult.data:
            print(f"\t{iter}")
