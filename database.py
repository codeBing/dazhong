#-*- coding:utf-8 -*-
"简单的操作数据库模块"

__author__ = 'BING'

import mysql.connector

class database(object):

    def __init__(self):
        self.connectStr = r"user='root',password='123456',database='dazhong',use_unicode=True"

    def connect(self):
        self.conn = mysql.connector.connect(user='root',password='123456',database='dazhong',use_unicode=True)
        self.cursor = self.conn.cursor()

    def insert(self,comments):
        try:
            self.cursor.execute('insert into comments values (%s,%s ,%s)', comments)
            self.conn.commit()
        except IOError, e:
            print e.message

    def close(self):
        self.cursor.close()
        self.conn.close()

