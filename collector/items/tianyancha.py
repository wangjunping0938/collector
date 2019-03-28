# -*- coding: utf-8 -*-
import scrapy


class TianyanchaItem(scrapy.Item):

    # 基本信息
    company = scrapy.Field()  # 企业基础信息
    number = scrapy.Field()  # 编号
    name = scrapy.Field()  # 企业全称
    short_name = scrapy.Field()  # 企业简称
    url = scrapy.Field()  # 企业官网URL
    logo_url = scrapy.Field()  # 企业LOGO URL
    scale_label = scrapy.Field()  # 企业规模
    nature_label = scrapy.Field()  # 企业性质
    advantage = scrapy.Field()  # 企业优势亮点
    description = scrapy.Field()  # 企业简述
    wx_public_no = scrapy.Field()  # 微信公众号ID
    wx_public = scrapy.Field()  # 微信公众号name
    wx_public_qr = scrapy.Field()  # 微信公众号二维码URL
    remark = scrapy.Field()  # 人工备注
    craw_user_id = scrapy.Field()  # 负责人ID
    tags = scrapy.Field()  # 标签(,分割)
    cida_credit_rating = scrapy.Field()  # 工会认证(Integer,0=无,1=A级,2=AA级,3=AAA级)
    is_high_tech = scrapy.Field()  # 高新企业(0=否,1=是)
    is_design_center = scrapy.Field()  # 设计中心(0=否,1=省级,2=国家级)
    ty_score = scrapy.Field()  # 天眼查评分
    ty_view_count = scrapy.Field()  # 天眼查浏览次数
    company_status_label = scrapy.Field()  # 公司状态
    ty_last_time = scrapy.Field()  # 天眼查最后更新日期

    # 联系人信息
    province = scrapy.Field()  # 省份
    city = scrapy.Field()
    address = scrapy.Field()  # 地址
    zip_code = scrapy.Field()  # 邮编
    contact_name = scrapy.Field()  # 联系人姓名
    contact_phone = scrapy.Field()  # 联系人电话
    contact_email = scrapy.Field()  # 联系人邮箱
    tel = scrapy.Field()  # 公司电话

    # 企业注册信息
    founder = scrapy.Field()  # 企业法人代表
    founder_desc = scrapy.Field()  # 创始人简介
    registered_capital = scrapy.Field()  # 注册资金
    registered_time = scrapy.Field()  # 注册日期
    company_count = scrapy.Field()  # 公司数量
    company_type = scrapy.Field()  # 企业类型
    registration_number = scrapy.Field()  # 工商注册号
    credit_code = scrapy.Field()  # 统一信用代码
    identification_number = scrapy.Field()  # 纳税人识别号
    industry = scrapy.Field()  # 行业
    business_term = scrapy.Field()  # 营业期限
    issue_date = scrapy.Field()  # 核准日期
    registration_authority = scrapy.Field()  # 登记机关
    english_name = scrapy.Field()  # 英文名称
    registered_address = scrapy.Field()  # 注册地址
    scope_business = scrapy.Field()  # 经营范围
    organization_code = scrapy.Field()  # 组织机构代码

    # 企业背景
    key_personnel_count = scrapy.Field()  # 主要人员数量
    shareholder_count = scrapy.Field()  # 股东信息数量
    investment_abroad_count = scrapy.Field()  # 对外投资数量
    annual_return_count = scrapy.Field()  # 公司年报数量
    chage_record_count = scrapy.Field()  # 变更记录数量
    affiliated_agency_count = scrapy.Field()  # 分支机构数量

    # 公司发展
    financing_count = scrapy.Field()  # 融资数量
    core_team_count = scrapy.Field()  # 核心团队数量
    enterprise_business_count = scrapy.Field()  # 企业业务数量
    investment_events_count = scrapy.Field()  # 投资事件数量
    competitor_count = scrapy.Field()  # 竞品信息数量

    # 司法风险
    action_at_law_count = scrapy.Field()  # 法律诉讼数量
    court_announcement_count = scrapy.Field()  # 法院公告数量
    dishonest_person_count = scrapy.Field()  # 失信人数量
    person_subject_count = scrapy.Field()  # 被执行人数量
    announcement_court_count = scrapy.Field()  # 开庭公告数量

    # 经营风险
    abnormal_operation_count = scrapy.Field()  # 经营异常数量
    administrative_penalty_count = scrapy.Field()  # 行政处罚数量
    break_law_count = scrapy.Field()  # 严重违法数量
    equity_pledged_count = scrapy.Field()  # 股权出质数量
    chattel_mortgage_count = scrapy.Field()  # 动产抵押数量
    tax_notice_count = scrapy.Field()  # 欠税公告数量
    judicial_sale_count = scrapy.Field()  # 司法拍卖数量

    # 经营状况
    bid_count = scrapy.Field()  # 招投标数量
    tax_rating_count = scrapy.Field()  # 税务评级数量
    product_count = scrapy.Field()  # 产品信息数量
    import_and_export_credit_count = scrapy.Field()  # 进出口信用数量
    certification_count = scrapy.Field()  # 资质证书数量
    wx_public_count = scrapy.Field()  # 微信公众号数量

    # 知识产权
    trademark_count = scrapy.Field()  # 商标数量
    patent_count = scrapy.Field()  # 专利数量
    software_copyright_count = scrapy.Field()  # 软件著作权数量
    works_copyright_count = scrapy.Field()  # 作品著作权数量
    icp_count = scrapy.Field()  # 网站备案数量
