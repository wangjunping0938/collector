# -*- coding: utf-8 -*-
import logging
from collector.middlewares.sqlitehandle import SqliteHandle
from collector.middlewares.redishandle import RedisHandle


class XiaomiyoupinPipline(object):
    def process_item(self, item, spider):
        RH = RedisHandle(spider.host, spider.port)
        dbfile = '{}/{}.sqlite'.format(spider.temp, spider.name)
        SH = SqliteHandle(dbfile)
        tablemodel = self.model()
        SH.create_table(spider.name, tablemodel)
        try:
            message = SH.insert(spider.name, item)
            logging.info('{} SUCCESS'.format(message))
            RH.insert(spider.name, item['url'])
        except Exception as e:
            logging.error(e)
        SH.close()
        return item

    def model(self):
        columns = list()
        columns.append('id integer primary key autoincrement')
        columns.append('category text not null')
        columns.append('sub_category text not null')
        columns.append('url text unique not null')
        columns.append('title text unique not null')
        columns.append('price integer not null')
        columns.append('comment_count integer')
        columns.append('favorable_rate integer')
        columns.append('star_level integer')
        return columns
