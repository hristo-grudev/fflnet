import scrapy

from scrapy.loader import ItemLoader

from ..items import FflnetItem
from itemloaders.processors import TakeFirst


class FflnetSpider(scrapy.Spider):
	name = 'fflnet'
	allowed_domains = ['www.ffl.net']
	start_urls = ['https://www.ffl.net/About-Us/News']

	def parse(self, response):
		post_links = response.xpath('//article//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="UnselectedNext"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//main[@class="body-content"]//div[@class="row"]//text()[normalize-space() and not(ancestor::h1 | ancestor::span[@class="sr-only"] | ancestor::strong | ancestor::p[contains(text(), "|")])]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//p[contains(text(), "|")]/text()').get()
		if date:
			date = date.split('|')[0]

		item = ItemLoader(item=FflnetItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
