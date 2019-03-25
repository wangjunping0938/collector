# -*- coding: utf-8 -*-
#
# Data query submission interface function
from collector.middlewares.parsefile import ParseFile as PF
from scrapy.utils.project import get_project_settings


class Interface(object):

    def __init__(self):
        settings = get_project_settings()
        self.webinterface  = PF.parse2dict(settings['CONFIG_FILE'],
                                           'webinterface')

    def company_list(self, field=['_id', 'name', 'number']):
        # 获取全部公司信息,过滤后只保留部分字段信息
        url = self.webinterface['company_list']
        parameters = {'per_page':requests.get(url).json()['data']['total_count']}
        data = requests.get(url, parameters).json()['data']['rows']
        # 根据条件过滤
        data = [d for d in data if d['status'] == 1]
        data = [{k:v for k, v in d.items() if k in field} for d in data]
        return data
