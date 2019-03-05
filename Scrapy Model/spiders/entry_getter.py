# -*- coding: utf-8 -*-
import scrapy
import re
from loginform import fill_login_form


class EntryGetterSpider(scrapy.Spider):
    name = 'entry_getter'
    allowed_domains = ['eksisozluk.com']

    start_urls = ['http://eksisozluk.com/entry/%s' % i for i in range(1,1000)]
    # if you want a single entry where 15 is the entry id
    #start_urls = ['http://eksisozluk.com/entry/147']

    login_url = 'http://eksisozluk.com/giris'

    login_user = 'sonerabay@ikudeeplearning.com'
    
    login_password = 'xxxxxxxxxx'

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

    def preprocess_text(self,text):

        # Deletes the remaining html data within text
        text = re.sub('<[^>]+>', ' ', text)
        # Deletes urls within the text
        text = re.sub(r'http\S+', '', text)
        # Replaces double back slashes
        text = text.replace("\\", "")
        # Deletes unnecassary beginings and endings
        text = text[9:-7]
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

        entry = response.xpath("string(//div[@class='content'])").extract()
        entry = str(entry)
        entry = self.preprocess_text(entry)

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
