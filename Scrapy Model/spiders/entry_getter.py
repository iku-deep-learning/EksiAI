# -*- coding: utf-8 -*-
import scrapy
import re


class EntryGetterSpider(scrapy.Spider):
    name = 'entry_getter'
    allowed_domains = ['eksisozluk.com/entry/2']

    start_urls = ['http://eksisozluk.com/entry/%s' % i for i in range(1,150)]
    #start_urls = ['http://eksisozluk.com/entry/15']

    def preprocess_text(self,text):

        garbage_text = ["\\","['<div class=\"content\">rn    ",  "rn  </div>']", "class=\"b\"", "<br>"]
        for garbage in garbage_text:
            text = text.replace(garbage,"")
        return text

    def extract_link(self,text):

        link = re.findall(r'<a  href[^<]+?</a>', text)
        link_names = re.findall(r'">([^<]+?)</a>', text)
        text = re.sub(r'<a  href([^<]+?)</a>', lambda match: link_names.pop(0), text, count=len(link_names))
        return text, link

    def parse(self, response):

        topic = response.xpath("//span[@itemprop='name']/text()").extract()
        topic = str(topic)
        topic = topic[2:len(topic)-2]


        entry = response.xpath("//div[@class='content']").extract()
        entry = str(entry)
        entry = self.preprocess_text(entry)

        entry, link = self.extract_link(entry)

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
            "link" : link,
            "entryDate": entry_date

        }
