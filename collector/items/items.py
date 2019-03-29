# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CollectorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class MaterialBankItem(scrapy.Item):
    title = scrapy.Field()    # 标题
    name = scrapy.Field()    # 图片名称
    img_url = scrapy.Field()    # 图片URL
    url = scrapy.Field()    # 原文地址
    tags = scrapy.Field()    # 标签
    color_tags = scrapy.Field()    # 颜色标签
    material_tags = scrapy.Field()    # 材质标签
    technique_tags = scrapy.Field()    # 工艺标签
    brand_tags = scrapy.Field()    # 品牌标签
    style_tags = scrapy.Field()    # 风格标签
    other_tags = scrapy.Field()    # 其他标签
    designer = scrapy.Field()    # 设计师
    company = scrapy.Field()    # 公司
    prize = scrapy.Field()    # 奖项名称
    prize_level = scrapy.Field()    # 奖项级别
    prize_time = scrapy.Field()    # 奖项时间
    brand_id = scrapy.Field()    # 品牌ID
    prize_id = scrapy.Field()    # 奖项ID
    info = scrapy.Field()    # 额外信息
    evt = scrapy.Field()    # 贡献者
    channel = scrapy.Field()    # 渠道

