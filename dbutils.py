# -*- coding: utf-8 -*-
import json
import pymysql

mysql_config = {
    "host": "192.168.1.100",
    "port": 4407,
    "userName": "test",
    "password": "test",
    "dbName": "demo",
    "charsets": "UTF8"
}

class PageResult:
    """MySQL 分页查询结果"""

    def __init__(self, page: int, page_size: int = 10):
        # 当前页面，从1开始
        self.page = page
        
        # 每页数据量， 默认显示10条
        self.page_size = page_size
        
        # 分页结束
        self.eop = False
        
        # 当前页数据
        self.data = []
        
        # 总记录数
        self.records = 0
        
        # 总页数
        self.pages = 0
        
        # 分页结束
        self.eop = False

    def load_page_data(self, data: [], records: int):
        # 当前页数据
        self.data = data
        
        # 总记录数
        self.records = records
        
        # 总页数
        self.pages = (records - 1) // self.page_size + 1 if records > 0 else 0
        
        if records == 0:
            self.page = 0
        
        # 分页结束
        self.eop = self.page == self.pages


class DBUtil:
    """MySQL 工具类"""
    _instance = None
    
    db = None
    cursor = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DBUtil, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.host = mysql_config['host']
            self.port = mysql_config['port']
            self.userName = mysql_config['userName']
            self.password = mysql_config['password']
            self.dbName = mysql_config['dbName']
            #self.charsets = mysql_config['charsets']
            print("配置文件：" + json.dumps(mysql_config))
    
    @staticmethod
    def INS():
        return DBUtil()

    # 链接数据库
    def get_con(self):
        """获取数据库连接"""
        self.db = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.userName,
            passwd=self.password,
            db=self.dbName
        )
        self.cursor = self.db.cursor()

    # 关闭链接
    def close(self):
        self.cursor.close()
        self.db.close()

    # 主键查询数据
    def get_one(self, sql):
        res = None
        try:
            self.get_con()
            self.cursor.execute(sql)
            res = self.cursor.fetchone()
            self.close()
        except Exception as e:
            print("查询失败！" + str(e))
        return res

    # 查询列表数据
    def get_all(self, sql, page: int, page_size: int = 10) -> PageResult:
        result = PageResult(page, page_size)
        try:
            fields = sql[len("select "):sql.lower().index(' from')]
            sql_records = sql.replace(fields, "COUNT(1)")

            offset = (page - 1) * page_size
            sql = sql + f" limit {offset}, {page_size}"

            self.get_con()
            self.cursor.execute(sql_records)
            records = self.cursor.fetchone()[0]

            if records > 0:
                self.cursor.execute(sql)
                data = self.cursor.fetchall()
                self.close()
            else:
                data = []

            result.load_page_data(data, records)
        except Exception as e:
            print("查询失败！" + str(e))
        return result

    # 插入数据
    def __insert(self, sql):
        count = 0
        try:
            self.get_con()
            count = self.cursor.execute(sql)
            self.db.commit()
            self.close()
        except Exception as e:
           print("操作失败！" + str(e))
           self.db.rollback()
        return count

    # 保存数据
    def save(self, sql):
        return self.__insert(sql)

    # 更新数据
    def update(self, sql):
        return self.__insert(sql)

    # 删除数据
    def delete(self, sql):
        return self.__insert(sql)
