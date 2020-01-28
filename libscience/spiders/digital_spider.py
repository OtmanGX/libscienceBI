import scrapy
from libscience.items import LibscienceItem
from scrapy_splash import SplashRequest


class DigitalSpider(scrapy.Spider):
	name = 'digital'
	topic = "None"
	
	ITEM_PIPELINES = {
		'myproject.pipelines.PricePipeline': 300,
		'myproject.pipelines.JsonWriterPipeline': 800,
	}

	script = """
	function main(splash)
		splash:wait(1)
		splash:runjs('document.querySelector("a.loa__link w-slide__btn tab-link slide-active").click()')
		splash:wait(1)
		return {
			html = splash:html(),
		}
	end
	"""

	def __init__(self , keywords=None , topic=None , *args , **kwargs) : 
		super(DigitalSpider , self).__init__(*args,**kwargs)
		self.start_urls = ['https://dl.acm.org/action/doSearch?AllField=%s' %keywords]
		self.topic = topic

	def start_requests(self):
		for url in self.start_urls:
			yield SplashRequest(url, self.parse, args={'wait': 2})

	def parse(self, response):
		for article in response.css('a::attr(href)'):
			# for each article go to article details new request get response parse store
			# yield {'title': article.css('a.result-list-title-link').extract_first()}
			if '/doi/abs' in article.extract(): 
				yield SplashRequest('https://dl.acm.org/' + article.extract(),self.parse_article, args={'lua_source': self.script, 'wait': 3})
				
		#for next_page in response.css('a.next::attr("href")'):
		#	yield response.follow(next_page, self.parse)

	def parse_article(self,response) : 
		item = LibscienceItem()
		# response conains the article details page
		title = response.css('.citation__title::text').extract_first() 

		authors = ";".join(response.css('.loa__author-name').css('span::text').extract())
		location = response.css('.publisher__address::text')
		abstract = response.css('.abstractInFull').css('p::text').extract_first()

		#affiliation_name = response.css('.affiliation_name::text').extract_first() if response.css('.affiliation_name::text').extract_first() is not None else ""
		#affiliation_city = response.css('.affiliation__city::text').extract_first() if response.css('.affiliation__city::text').extract_first() is not None else ""
		#affiliation_country = response.css('.affiliation__country::text').extract_first() if response.css('.affiliation__country::text').extract_first() is not None else "USA"
		journal = response.css('.journal-meta').css('.serial-title::text').extract_first()
		
		pub_year = response.css('.section__separator>.section__content>.rlist').css('li::text').extract()
		item['title']= title
		item['authors']= ''.join(authors) 
		item['abstract_']= abstract
		item['country']= ''.join(location.extract()).split(', ')[2]
		item['date_pub'] = ''.join(pub_year[0]).split(' ')[3]
		item['topic'] = self.topic		
		item['latitude'] =  0
		item['longtitude'] = 0
		item['journal'] = journal
		yield item
