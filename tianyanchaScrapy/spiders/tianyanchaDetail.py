#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'stringk'
__mtime__ = '2018/9/26'
# qq:2456056533

佛祖保佑  永无bug!

"""
import scrapy
# from scrapy_redis.spiders import RedisSpider
# from scrapy_redis.utils import bytes_to_str

from scrapy_redis_bloomfilter.spiders import RedisSpider
from scrapy_redis_bloomfilter.utils import bytes_to_str

from tianyanchaScrapy.spiders.tianyancha import string_to_dict
from tianyanchaScrapy.items import TianyanchascrapyItem


tydetail_spider = 'tydetail'


class TianyanchaDetailSpider(RedisSpider):
    name = tydetail_spider
    allowed_domains = ['tianyancha.com']
    redis_key = 'tyc:request'

    cookies={}

    custom_settings = {'DOWNLOADER_MIDDLEWARES': {'tianyanchaScrapy.middlewares.UserAgentDownloaderMiddleware': 543, },
                       'ITEM_PIPELINES':{'tianyanchaScrapy.pipelines.TianyanchascrapyPipeline': 300,}
                       }

    def make_request_from_data(self, data):
        url = bytes_to_str(data,self.redis_encoding)
        # lpush tyc:request https://www.tianyancha.com/company/1150018629 https://www.tianyancha.com/company/1077215780
        return self.make_requests_from_url(url)

    def make_requests_from_url(self, url):
        self.cookies = string_to_dict()  # 加入登入态, 同样这里还可以加入meta
        self.logger.info('爬取:',url)
        return scrapy.Request(url, callback=self.detail_parse, cookies=self.cookies, dont_filter=True)

    def detail_parse(self,response):
        item = TianyanchascrapyItem()
        item['url'] = response.url
        item['logo_ico'] = response.xpath('//div[@class="logo -w100"]/img/@data-src').extract_first()
        item['centent_title'] = response.xpath('//div[@class="header"]/h1/text()').extract_first()

        detail= response.xpath('//div[@class="detail "]')
        item['centent_mobile'] = detail.xpath('div/div/span[2]/text()').extract_first()
        item['centent_email'] = detail.xpath('div/div[2]/span[2]/text()').extract_first()
        item['centent_index'] = detail.xpath('div[2]/div/a/@href').extract_first()
        centent_address = detail.xpath('div[2]/div[2]/span[2]/@title').extract_first()
        if not centent_address:
            centent_address = detail.xpath('div[2]/div[2]/text()').extract_first()
        item['centent_address'] = centent_address

        item['faren'] = response.xpath('//div[@class="humancompany"]/div/a/@title').extract_first()

        tr = response.xpath('//table[@class="table -striped-col -border-top-none"]/tbody')
        d1 = tr.xpath('tr[1]/td[2]/text()').extract_first()
        d2 = tr.xpath('tr[1]/td[4]/text()').extract_first()

        d3 = tr.xpath('tr[2]/td[2]/text()').extract_first()
        d4 = tr.xpath('tr[2]/td[4]/text()').extract_first()

        d5 = tr.xpath('tr[3]/td[2]/text()').extract_first()
        d6 = tr.xpath('tr[3]/td[4]/text()').extract_first()

        d7 = tr.xpath('tr[4]/td[2]/span/text()').extract_first()
        d8 = tr.xpath('tr[4]/td[4]/text/text()').extract_first()

        d9 = tr.xpath('tr[5]/td[2]/text()').extract_first()
        d10 = tr.xpath('tr[5]/td[4]/text()').extract_first()

        d11 = tr.xpath('tr[6]/td[2]/text()').extract_first()
        d12 = tr.xpath('tr[6]/td[4]/text()').extract_first()

        d13 = tr.xpath('tr[7]/td[2]/text()').extract_first()
        d14 = tr.xpath('tr[7]/td[4]/text()').extract_first()

        d15 = tr.xpath('tr[8]/td[2]/text()').extract_first()
        d16 = tr.xpath('tr[9]/td[2]/span/span/span[1]/text()').extract_first()

        detail ={'工商注册号':d1,'组织机构代码':d2,'统一信用代码':d3,'公司类型':d4,'纳税人识别号':d5,'行业':d6,'营业期限':d7,'核准日期':d8,'纳税人资质':d9,'人员规模':d10,'实缴资本':d11,'登记机关':d12,'参保人数':d13,'英文名称':d14,'注册地址':d15,'经营范围':d16}
        item['detail'] = detail

        item['license'] = ''
        license_url = response.xpath('//div[@id="nav-main-baseInfo"]/a/@href').extract_first()
        if license_url:
            yield scrapy.Request(license_url, callback=self.detail2_parse, cookies=self.cookies, meta={'item': item},
                                 dont_filter=True)
        else:
            yield item


    def detail2_parse(self, response):
        item = response.meta['item']
        item['license'] = response.xpath('//*[@id="web-content"]/div/div/div[1]/div[2]/img/@src').extract_first()
        return item
