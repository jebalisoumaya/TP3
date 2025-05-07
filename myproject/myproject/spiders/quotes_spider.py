from pathlib import Path
import scrapy
from scrapy.loader import ItemLoader
from myproject.items import MyprojectItem
import logging

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
    ]

    def parse(self, response):
        self.log(f'Parsing page: {response.url}')
        
        # Extract quotes using ItemLoader
        for quote in response.css('div.quote'):
            loader = ItemLoader(item=MyprojectItem(), selector=quote)
            loader.add_css('text', 'span.text::text')
            loader.add_css('author', 'small.author::text')
            loader.add_css('tags', 'a.tag::text')
            yield loader.load_item()
        
        # Handle pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            self.log(f'Next page: {next_page}')
            yield response.follow(next_page, callback=self.parse)







""" 
    def parse(self, response):
        
        next_page = response.css('li.next a::attr(href)').get()
        self.log(f'Next page: {next_page}')
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('a.tag::text').getall(),
            }
        next_page = response.urljoin(next_page)
       
        yield scrapy.Request(next_page, callback=self.parse)

        #Approach 1: Selects only the "next" link with li.next a::attr(href)
        #Approach 2: Selects all links in the pagination with ul.pager a::attr(href)

def parse(self, response):
    next_page = response.css('li.next a::attr(href)').get()
    
    for quote in response.css('div.quote'):
        yield {
            'text': quote.css('span.text::text').get(),
            'author': quote.css('small.author::text').get(),
            'tags': quote.css('div.tags a.tag::text').getall(),
        }
    
    for href in response.css('ul.pager a::attr(href)'):
        yield response.follow(href, callback=self.parse)"""
   