# -*- coding: utf-8 -*-
import json
import pymysql

mysql_config = {
    "host": "192.168.1.102",
    "port": 4407,
    "userName": "test",
    "password": "test",
    "dbName": "demo",
    "charsets": "UTF8"
}

class DBUtil:
    """MySQL 工具类"""
    db = None
    cursor = None

    def __init__(self):
        self.host = mysql_config['host']
        self.port = mysql_config['port']
        self.userName = mysql_config['userName']
        self.password = mysql_config['password']
        self.dbName = mysql_config['dbName']
        #self.charsets = mysql_config['charsets']
        print("配置文件：" + json.dumps(mysql_config))

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
    def get_all(self, sql):
        res = None
        try:
            self.get_con()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            self.close()
        except Exception as e:
            print("查询失败！" + str(e))
        return res

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
