# -*- coding: utf-8 -*-
#
# Data query submission interface function
import requests
import logging


class Interface(object):

    @staticmethod
    def company_view(url, company):
        # 获取公司详情
        parameters = {'number':company['number']}
        try:
            response = requests.get(url, parameters).json()['data']
            return response
        except Exception as e:
            logging.error(e)

    @staticmethod
    def company_list(url, field=['_id', 'name', 'number']):
        # 获取全部公司信息,过滤后只保留部分字段信息
        per_page = requests.get(url).json()['data']['total_count']
        parameters = {'per_page':per_page}
        data = requests.get(url, parameters).json()['data']['rows']
        data = [d for d in data if d['status'] == 1]
        data = [{k:v for k, v in d.items() if k in field} for d in data]
        return data

    @staticmethod
    def company_queue_list(url, status_name, status=(1, 5)):
        # 获取待更新队列中的公司列表,并过滤不符合条件的公司
        per_page = requests.get(url).json()['data']['total_count']
        parameters = {'in_grap':5, 'per_page':per_page}
        data = requests.get(url, parameters).json()['data']['rows']
        data = [d for d in data if d['status'] == 1]
        rst = [d for d in data if d[status_name] not in status]
        return rst

    @staticmethod
    def query_status(url, company, status=['tyc_status', 'bd_status']):
        # 查询公司信息爬取状态
        parameters = {'in_grap':5, 'number':company['number']}
        data = requests.get(url, parameters).json()['data']['rows'][0]
        rst = {k:v for k, v in data.items() if k in status}
        return list(rst.values())

    @staticmethod
    def update_status(url, company, status, value):
        # 更新公司信息爬取状态
        parameters = {'id':company['_id'], status:value}
        try:
            message = requests.post(url, parameters).json()['message']
            if message == 'success!':
                message = '{}: update {} {}'.format(company['name'], status, message)
                rst = True
            else:
                message = '{}: update {} {}'.format(company['name'], status, message)
                rst = False
            logging.info(message)
        except Exception as e:
            logging.error(e)
            rst = False
        return rst

    @staticmethod
    def updata_out_grap(url, company, status):
        # 根据其他爬取状态变化更新站外爬取状态值
        parameters = {'id':company['_id']}
        if 1 in status:
            parameters['out_grap'] = 1  # 进行中
        elif sum(status) == 10:
            parameters['out_grap'] = 5  # 已完成
        elif sum(status) in (4, 7):
            parameters['out_grap'] = 2  # 失败
        elif sum(status) in (0, 2, 5):
            parameters['out_grap'] = 0  #未抓取
        try:
            message = requests.post(url, parameters).json()['message']
            if message == 'success!':
                message = '{}: update out_grap {}'.format(company['name'], message)
                rst = True
            else:
                message = '{}: update out_grap {}'.format(company['name'], message)
                rst = False
            logging.info(message)
        except Exception as e:
            logging.error(e)
            rst = False
        return rst

    @staticmethod
    def update_data(url, data):
        # 上传爬取的公司信息数据
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

    @staticmethod
    def upload_image_info(url, data):
        # 上传图片信息
        try:
            message = requests.post(url, data).json()['message']
            if message == 'success!':
                message = 'Picture info upload {}'.format(message)
                rst = True
            else:
                message = 'Picture info upload {}'.format(message)
                rst = False
            logging.info(message)
        except Exception as e:
            logging.error(e)
            rst = False
        return rst


if __name__ == '__main__':
    opalus_cpy_list = 'http://example.com/interface/design_cpy/list'
    opalus_queue_list = 'http://example.com/interface/cpy_queue/list'
    opalus_queue_submit = 'http://example.com/interface/cpy_queue/submit'
    opalus_cpy_view = 'http://example.com/interface/design_cpy/view'
    opalus_cpy_update = 'http://example.com/interface/design_cpy/update'
    opalus_image_submit = 'http://example.com/interface/image/submit'

    """
    cpys = Interface.company_list(opalus_company_list)

    company = {'_id': '5a951f5db24b006f0fe723f2', 'name': '北京上品极致产品设计有限公司', 'number': 180227170533300348}
    cpyv = Interface.company_view(opalus_company_view, company)
    print(cpyv)

    cqltyc = Interface.company_queue_list(opalus_queue_list, 'tyc_status')
    print(cqltyc)
    cqlbd = Interface.company_queue_list(opalus_queue_list, 'bd_status')
    print(cqlbd)

    company = {'_id':'5b3b3271b24b005a46d493fc', 'name':'嘉兰图设计股份有限公司', 'number':180621164746444014}
    Interface.update_status(opalus_queue_submit, company, 'bd_status', 0)
    Interface.update_status(opalus_queue_submit, company, 'tyc_status', 0)

    cqlc = Interface.query_status(opalus_queue_list, company)
    print(cqlc)
    Interface.updata_out_grap(opalus_queue_submit, company, cqlc)
    """
