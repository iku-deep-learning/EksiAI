# -*- coding: utf-8 -*-
import scrapy


class EntryGetterSpider(scrapy.Spider):
    name = 'entry_getter'
    allowed_domains = ['eksisozluk.com/entry/2']

    start_urls = ['http://eksisozluk.com/entry/%s' % i for i in range(1,4)]

    def parse(self, response):

        topic = response.xpath("//span[@itemprop='name']/text()").extract()
        entry = response.xpath("//div[@class='content']/text()").extract()

        yield {

            "topic": topic,
            "entry": entry

        }
