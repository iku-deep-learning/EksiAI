# -*- coding: utf-8 -*-
import scrapy
import re


class EntryGetterSpider(scrapy.Spider):
    name = 'entry_getter'
    allowed_domains = ['eksisozluk.com/entry/2']

    start_urls = ['http://eksisozluk.com/entry/%s' % i for i in range(1,150)]
    #start_urls = ['http://eksisozluk.com/entry/15']

    def parse(self, response):

        topic = response.xpath("//span[@itemprop='name']/text()").extract()
        topic = str(topic)
        topic = topic[2:len(topic)-2]


        entry = response.xpath("//div[@class='content']").extract()
        entry = str(entry)
        if "class=\"b\"" in entry:
            entry = entry.replace("class=\"b\"", "")
        c = '\\'
        position = [pos for pos, char in enumerate(entry) if char == c]
        entry_list = list(entry)
        for index in position:
            entry_list[index] = 'A'
        entry = "".join(entry_list)
        entry = entry[31:len(entry)-15]

        author = response.xpath("//a[@class='entry-author']/text()").extract()
        author = str(author)
        author = author[2:len(author) - 2]

        # this returns a list e.g [/entry/2]
        entry_id = response.xpath("//a[@class='entry-date permalink']/@href").extract()
        # conversion to string '[/entry/2]'
        entry_id = str(entry_id)
        # only gets the digit value from /entry/xyzclc
        entry_id = str(re.search(r'\d+', entry_id).group(0))

        entry_date = response.xpath("//a[@class='entry-date permalink']/text()").extract()
        entry_date = str(entry_date)
        entry_date = entry_date[2:len(entry_date)-2]



        yield {

            "entryId":entry_id,
            "author": author,
            "topic": topic,
            "entry": entry,
            "entryDate": entry_date

        }
