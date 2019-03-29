# -*- coding: utf-8 -*-
import json
from collector.middlewares.interface import Interface


class RedDotPipline(object):

    def process_item(self, item, spider):
        api = spider.apis['opalus_image_submit']
        Interface.upload_image_info(api, item):
        item = self.finish_data(item)
        return item

    def finish_data(self, item):
        # 设计师信息
        handle = lambda d: ','.join(list(map(lambda x: '%s:%s' % (x['label'],x['value']), d)))
        keys = ('designer',)
        item.update({k:handle(v) for k,v in item.items() if k in keys})

        # 图片链接
        handle = lambda d: d.replace('&usage=hero', '')
        keys = ('img_url',)
        item.update({k:handle(v) for k,v in item.items() if k in keys})

        # 其他信息
        handle = lambda d: json.dumps(d)
        keys = ('info',)
        item.update({k:handle(v) for k,v in item.items() if k in keys})

        return item
