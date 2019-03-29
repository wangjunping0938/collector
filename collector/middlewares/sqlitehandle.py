# -*- coding: utf-8 -*-
#
# SQLite database process
import sqlite3


class SqliteHandle(object):

    def __init__(self, dbfile):
        self.conn = sqlite3.connect(dbfile)
        self.curs = self.conn.cursor()

    def create_table(self, tablename, columns):
        column = ', '.join(columns)
        sql = 'create table if not exists %s (%s)' % (tablename, column)
        self.curs.execute(sql)
        self.conn.commit()
        return sql

    def insert(self, tablename, data):
        keys = ', '.join(data.keys())
        values = tuple(data.values())
        sql = 'insert into %s (%s) values %s' % (tablename, keys, values)
        self.curs.execute(sql)
        self.conn.commit()
        return sql

    def fetch_one(self, tablename, key, value):
        sql = 'select * from %s where %s = "%s"' % (tablename, key, value)
        self.curs.execute(sql)
        rst = self.curs.fetchall()
        return rst

    def fetch_all(self, tablename):
        sql = 'select * from {}'.format(tablename)
        self.curs.execute(sql)
        rst = self.curs.fetchall()
        return rst

    def update(self, tablename, key, skey, data):
        sql = 'update %s set %s = ? where %s = ?' % (tablename, key, skey)
        self.curs.execute(sql, data)
        self.conn.commit()
        return sql

    def close(self):
        self.curs.close()
        self.conn.close()
