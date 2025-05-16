# -*- coding: utf-8 -*-
import json

from order import OrderManager
from test_result import TestResultManager

def load_order():
    page = 1
    page_size = 50
    pageResult = OrderManager.list(page, page_size)
    print(f"get_all执行结果：{pageResult.page}/{pageResult.pages} 每页显示{pageResult.page_size}条，总记录数{pageResult.records}条")
    for iter in pageResult.data:
        print(f"\t{iter}")
    
    #while(not pageResult.eop):
    #    page = page + 1
    #    pageResult = OrderManager.list(page, page_size)
    #    print(f"get_all执行结果：{pageResult.page}/{pageResult.pages} 每页显示{pageResult.page_size}条，总记录数{pageResult.records}条")
    #    for iter in pageResult.data:
    #        print(f"\t{iter}")


def load_test_result():
    page = 1
    page_size = 50
    pageResult = TestResultManager.list(page, page_size)
    print(f"get_all执行结果：{pageResult.page}/{pageResult.pages} 每页显示{pageResult.page_size}条，总记录数{pageResult.records}条")
    for iter in pageResult.data:
        print(f"\t{iter}")
    
    #while(not pageResult.eop):
    #    page = page + 1
    #    pageResult = OrderManager.list(page, page_size)
    #    print(f"get_all执行结果：{pageResult.page}/{pageResult.pages} 每页显示{pageResult.page_size}条，总记录数{pageResult.records}条")
    #    for iter in pageResult.data:
    #        print(f"\t{iter}")

if __name__ == '__main__':
    load_order()
    load_test_result()
