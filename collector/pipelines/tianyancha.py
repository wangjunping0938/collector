# -*- coding: utf-8 -*-
#
# https://www.tianyancha.com公司信息数据处理
import os
import re
import string
import logging
from fontTools.ttLib import TTFont
from collector.middlewares.interface import Interface as I
from collector.middlewares.redishandle import RedisHandle


class TianyanchaPipline(object):

    def process_item(self, item, spider):
        RH = RedisHandle(spider.host, spider.port)
        company = item['company']
        item.pop('company')
        item = self.collation_data(item)
        # 上传公司信息
        api = spider.apis['opalus_company_update']
        if I.update_data(api, item):
            if spider.mode:
                # 更新天眼查爬虫状态
                api = spider.apis['opalus_queue_submit']
                I.update_status(api, company, 'tyc_status', 5)

                # 更新站外爬取状态
                api = spider.apis['opalus_queue_list']
                status = I.query_status(api, company)
                api = spider.apis['opalus_queue_submit']
                I.updata_out_grap(api, company, status)
            # Redis数据库记录d当前URL爬取状态
            RH.insert(spider.name, company['link'])
        else:
            logging.error('{}: Data upload failed'.format(company['name']))
        return item

    # 数据整理
    def collation_data(self, item):
        # 清理空数据
        clean_data = {k:v for k, v in item.items() if v}
        item.clear()
        item.update(clean_data)

        # 专利数量
        handle = lambda d: ''.join(re.findall('\d+', ''.join(d)))
        keys = ('patent_count')
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 微信相关数据整理
        handle = lambda d: ','.join(d)
        keys = ('wx_public_qr', 'wx_public', 'wx_public_no',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 邮箱相关数据整理
        handle = lambda d: ','.join(set(re.findall(r'(\w+@\w+\.\w+)', ''.join(d))))
        keys = ('contact_email',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 电话号码相关数据整理
        handle = lambda d: ','.join(set(re.findall(r'\d+-?\d*', ''.join(d))))
        keys = ('tel',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 公司地址相关数据整理
        handle = lambda d: sorted(
            d, key=lambda k: len(k))[-1].strip(string.punctuation)
        keys = ('address',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 公司数量数据整理
        handle = lambda d: ''.join(re.findall(r'\d+', ''.join(d)))
        keys = ('company_count',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 公司简介数据整理
        handle = lambda d: ''.join(d).strip()
        keys = ('description',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 英文名称相关数据整理
        ext = lambda d: re.findall('\w+', ''.join(d))
        handle = lambda d, k: d if ext(d[k]) else d.pop(k)
        try:
            handle(item, 'english_name')
        except Exception as e: pass

        # 浏览次数数据整理
        ext = lambda d: int(''.join(re.findall('\d+', ''.join(d))))
        handle = lambda d: ext(d) * 10000 if '万' in ''.join(d) else ext(d)
        keys = ('ty_view_count',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 高新企业数据整理
        handle = lambda d: 1 if d else 0
        keys = ('is_high_tech',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 核准日期(网页字体未被替换时注释改行)
        #item.update({key:self.parse_font(value) for key, value in item.items() if key == 'issue_date'})

        # 公司规模过滤
        def handle(d):
            if '-' in ''.join(d):
                n = ''.join(re.findall(r'[-\d]+', ''.join(d)))
            elif '小于' in ''.join(d):
                n = '0-{}'.format(''.join(re.findall(r'\d+', ''.join(d))))
            else:
                n = '{}+'.format(''.join(re.findall(r'\d+', ''.join(d))))
            return n
        keys = ('scale_label',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 注册资金数据整理
        ext = lambda d: ''.join(re.findall(r'[\.\d]+', ''.join(d)))
        def handle(d):
            if '万' in ''.join(d):
                n = '%.2f' % (float(ext(d)) * 10000)
            else:
                n = '%.2f' % (float(ext(d)))
            return n
        keys = ('registered_capital',)
        item.update({k:handle(v) for k, v in item.items() if k in keys})

        # 所有数据转换为字符串模式
        handle = lambda d: ''.join(d).strip() if isinstance(d, list) else d
        item.update({k:handle(v) for k, v in item.items()})

        # 清理整理完成后的空数据
        clean_data = {key:value for key, value in item.items() if value}
        item.clear()
        item.update(clean_data)
        return item

    def parse_font(self, value):
        # 解析字体还原数据
        fontfile = '%s/%s' % (self.temp, 'tyc-num.woff')
        if not os.path.exists(fontfile):
            return None
        font = TTFont(fontfile)
        source_num = font.getGlyphOrder()[2:10]
        target_num = font.getGlyphNames()[:8]
        value = list(''.join(value))
        for i, v in enumerate(value):
            if v in source_num:
                index = source_num.index(v)
                value[i] = target_num[index]
        return ''.join(value)
