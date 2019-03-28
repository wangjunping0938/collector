# -*- coding: utf-8 -*-
#
# Redis database operation method 
import redis
import logging


class RedisHandle(object):

    def __init__(self, host, port, password=None):
        self.conn = redis.Redis(host, port, password)

    def insert(self, name, url, value=1):
        self.conn.hset(name, url, value)
        logging.info('insert {}:{}:{}'.format(name, url, value))

    def query(self, name, url):
        rst = self.conn.hget(name, url)
        return rst

    def verify(self, name, url):
        rst = self.conn.hexists(name, url)
        return rst


if __name__ == '__main__':
    RH = RedisHandle('localhost', '6379')
    name = 'tyc'
    url = 'http://www.tyc.com'
    value = 1
    RH.insert(name, url, value)
    rst = RH.query(name, url)
    print(rst)
    rst = RH.verify(name, url)
    print(rst)
