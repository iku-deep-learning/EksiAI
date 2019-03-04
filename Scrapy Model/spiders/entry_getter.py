# -*- coding: utf-8 -*-
import scrapy


class EntryGetterSpider(scrapy.Spider):
    name = 'entry_getter'
    allowed_domains = ['eksisozluk.com/entry/2']

    start_urls = ['http://eksisozluk.com/entry/%s' % i for i in range(1,10000)]

    def parse(self, response):

        topic = response.xpath("//span[@itemprop='name']/text()").extract()
        topic = str(topic)
        # only first second to last 2nd element contains valid author name
        topic = topic[2:len(topic)-2]
        
        entry = response.xpath("//div[@class='content']/text()").extract()
        entry = str(entry)
        # only first 10th to last 8th element contains valid author name
        entry = entry[10:len(entry)-8]
        
        author = response.xpath("//a[@class='entry-author']/text()").extract()
        author = str(author)
        # only first second to last 2nd element contains valid author name
        author = author[2:len(author) - 2]

        # this returns a list e.g [/entry/2]
        entry_id = response.xpath("//a[@class='entry-date permalink']/@href").extract()
        # conversion to string '[/entry/2]'
        entry_id = str(entry_id)
        # only last 3rd element contains the real entry id
        entry_id = entry_id[len(entry_id)-3]
        
        yield {
            
            "entryId":entry_id,
            "author": author,
            "topic": topic,
            "entry": entry

        }
