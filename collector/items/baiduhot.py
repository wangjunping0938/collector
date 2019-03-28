# -*- coding: utf-8 -*-
import scrapy


class BaiduhotItem(scrapy.Item):
    name = scrapy.Field()  # 公司名称
    number = scrapy.Field()    # 公司编号
    baidu_hot = scrapy.Field()    # 百度热点(公司名称搜索)
    baidu_brand_hot = scrapy.Field()    # 百度热度(品牌名搜索)
    company = scrapy.Field()
