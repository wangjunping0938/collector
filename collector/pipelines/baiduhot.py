# -*- coding: utf-8 -*-
#
# 公司百度搜索热度信息处理
import logging
from collector.middlewares.interface import Interface as I
from collector.middlewares.redishandle import RedisHandle


class BaiduhotPipline(object):

    def process_item(self, item, spider):
        RH = RedisHandle(spider.host, spider.port)
        company = item['company']
        item.pop('company')
        # 上传数据
        api = spider.apis['opalus_company_update']
        if I.update_data(api, item):
            if spider.mode:
                # 更新百度热度爬取状态
                api = spider.apis['opalus_queue_submit']
                I.update_status(api, company, 'bd_status', 5)

                # 更新站外爬取状态
                api = spider.apis['opalus_queue_list']
                status = I.query_status(api, company)
                api = spider.apis['opalus_queue_submit']
                I.updata_out_grap(api, company, status)
            # redis数据库记录当前URL爬取状态(用作去重)
            RH.insert(spider.name, company['link'])
        else:
            logging.error('{}: Data upload failed'.format(company['name']))
        return item
