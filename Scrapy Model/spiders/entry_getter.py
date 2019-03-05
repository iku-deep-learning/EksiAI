# -*- coding: utf-8 -*-
import scrapy
import re
from loginform import fill_login_form
import html


class EntryGetterSpider(scrapy.Spider):
    name = 'entry_getter'
    allowed_domains = ['eksisozluk.com']

    #start_urls = ['http://eksisozluk.com/entry/%s' % i for i in range(1,120)]
    # if you want a single entry where 15 is the entry id
    start_urls = ['http://eksisozluk.com/entry/87398436']

    login_url = 'http://eksisozluk.com/giris'

    login_user = 'usermail'
    login_password = 'pass'

    def start_requests(self):
        # let's start by sending a first request to login page
        yield scrapy.Request(self.login_url, self.parse_login)

    def parse_login(self, response):
        # got the login page, let's fill the login form...
        data, url, method = fill_login_form(response.url, response.body,
                                            self.login_user, self.login_password)
        # ... and send a request with our login data
        return scrapy.FormRequest(url, formdata=dict(data),method=method, callback=self.start_crawl)

    def start_crawl(self, response):
        # OK, we're in, let's start crawling the protected pages
        for url in self.start_urls:
          yield scrapy.Request(url)

    def preprocess_text(self,text,url_text):

        garbage_text = ["\\","['<div class=\"content\">rn    ",  "rn  </div>']", "class=\"b\"", "<br>"]
        for garbage in garbage_text:
            text = text.replace(garbage,"")

        link_names = re.findall(r'">([^<]+?)</a>', text)
        for i, link in enumerate(link_names):
            link_names[i] = "`" + link + "`"

        text = re.sub(r'<a  href([^<]+?)</a>', lambda match: link_names.pop(0), text, count=len(link_names))
        # Deletes the remaining html data within text
        text = re.sub('<[^>]+>', ' ', text)
        # Deletes urls within the text
        text = re.sub(r'http\S+', '', text)

        # Cleaning also url text like click here
        text = text.replace(url_text,"")

        # Deleting multiple space and left new lines
        text = ' '.join(text.split())

        return text

    def preprocess_fav(self, fav_count):

        # fav count is a substring between the values below
        fav_count = re.search('data-favorite-count=\"(.*)\" data', fav_count).group(1)
        # only first part before space contains the fav count
        fav_count = fav_count.split(' ')[0]
        # deleting last back slash
        fav_count = fav_count[:-1]

        return fav_count

    def parse(self, response):

        topic = response.xpath("//span[@itemprop='name']/text()").extract()
        topic = str(topic)
        topic = topic[2:len(topic) - 2]

        entry = response.xpath("//div[@class='content']").extract()
        entry = str(entry)

        # we only get the text of an url like click here
        url_text = str(response.xpath("string(//a[@class='url']/text())").extract())
        url_text = url_text[2:-2]
        entry = self.preprocess_text(entry,url_text)
        # convert html unicode to string
        entry = html.unescape(entry)

        author = response.xpath("//a[@class='entry-author']/text()").extract()
        author = str(author)
        author = author[2:len(author) - 2]

        # this returns a list e.g [/entry/2]
        entry_id = response.xpath("//a[@class='entry-date permalink']/@href").extract()
        # conversion to string '[/entry/2]'
        entry_id = str(entry_id)
        # only gets the digit value from /entry/xyzclc
        entry_id = str(re.search(r'\d+', entry_id).group(0))

        # pre-processing the fav count
        fav_count = response.xpath("//li[@data-favorite-count]").extract()
        fav_count = self.preprocess_fav(str(fav_count))
        # it's more useful for us as an integer(to train the data)
        fav_count = int(fav_count)

        entry_date = response.xpath("//a[@class='entry-date permalink']/text()").extract()
        entry_date = str(entry_date)
        entry_date = entry_date[2:len(entry_date) - 2]

        yield {

          "entryId": entry_id,
          "author": author,
          "topic": topic,
          "entry": entry,
          "entryDate": entry_date,
          "favCount": fav_count
        }
