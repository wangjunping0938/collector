# -*- coding: utf-8 -*-
import scrapy


class XiaomiyoupinItem(scrapy.Item):
    category = scrapy.Field()  # 主类别
    sub_category = scrapy.Field()  # 子类别
    url = scrapy.Field()  # 商品链接
    title = scrapy.Field()  # 商品标题
    price = scrapy.Field()  # 商品价格
    comment_count = scrapy.Field()  # 品论数
    favorable_rate = scrapy.Field()  # 好评率
    star_level = scrapy.Field()  # 星级
