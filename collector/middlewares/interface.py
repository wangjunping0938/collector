# -*- coding: utf-8 -*-
#
# Data query submission interface function
import requests
import logging
from collector.middlewares.parsefile import ParseFile as PF
from scrapy.utils.project import get_project_settings


class Interface(object):

    def __init__(self):
        settings = get_project_settings()
        self.webinterface  = PF.parse2dict(settings['CONFIG_FILE'], 'webinterface')

    def company_list(self, field=['_id', 'name', 'number']):
        # 获取全部公司信息,过滤后只保留部分字段信息
        url = self.webinterface['company_list']
        parameters = {'per_page':requests.get(url).json()['data']['total_count']}
        data = requests.get(url, parameters).json()['data']['rows']
        # 根据条件过滤
        data = [d for d in data if d['status'] == 1]
        data = [{k:v for k, v in d.items() if k in field} for d in data]
        return data

    def company_queue_list(self, status_name, status=(1, 5)):
        # 获取待更新队列中的公司列表
        url = self.webinterface['company_queue_list']
        parameters = {'in_grap':5}
        parameters['per_page'] = requests.get(url).json()['data']['total_count']
        data = requests.get(url, parameters).json()['data']['rows']
        # 过滤不符合条件的公司
        data = [d for d in data if d['status'] == 1]
        rst = [d for d in data if d[status_name] not in status]
        return rst

    def update_status(self, company, status_name, status_value):
        # 更新公司信息爬取状态
        url = self.webinterface['company_queue_submit']
        parameters = {'id':company['id'], status_name:status_value}
        try:
            response = requests.post(url, parameters).json()
            if response['message'] == 'success!':
                message = '{}:爬取状态更新完成!'.format(company['name'])
            else:
                message = response['message']
            logging.info(message)
        except Exception as e:
            logging.error(e)

    def updata_out_grap(self, company, status=['tyc_status', 'bd_status']):
        # 根据其他爬取状态变化更新站外爬取状态值
        url = self.webinterface['company_queue_list']
        parameters = {'in_grap':5, 'number':company['number']}
        response = requests.get(url, parameters).json()['data']['rows'][0]
        status = (response[status[0]], response[status[1]])

        parameters = {'id':company['id']}
        if 1 in status:
            parameters['out_grap'] = 1  # 进行中
        elif sum(status) == 10:
            parameters['out_grap'] = 5  # 已完成
        elif sum(status) in (4, 7):
            parameters['out_grap'] = 2  # 失败
        elif sum(status) in (0, 2, 5):
            parameters['out_grap'] = 0  #未抓取

        # 更新站外爬取状态
        url = self.webinterface['company_queue_submit']
        try:
            response = requests.post(url, parameters).json()
            if response['message'] == 'success!':
                message = '{}: 站外爬取状态更新完成'.format(company_name)
                rst = True
            else:
                message = response['message']
                rst = False
            logging.info(message)
        except Exception as e:
            logging.error(e)
            rst = False
        return rst

    def update_data(self, data):
        # 上传爬取的公司信息数据
        url = self.webinterface['company_update']
        try:
            response = requests.post(url, data).json()
            if response['message'] == 'success!':
                message = '{}: 信息上传完成'.format(data['name'])
                rst = True
            else:
                message = response['message']
                rst = False
            logging.info(message)
        except Exception as e:
            logging.error(e)
            rst = False
        return rst
