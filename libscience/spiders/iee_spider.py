import scrapy
from libscience.items import LibscienceItem
from scrapy_splash import SplashRequest


class IeeSpider(scrapy.Spider):
	name = 'iee'
	topic = "None"
	
	ITEM_PIPELINES = {
		'myproject.pipelines.PricePipeline': 300,
		'myproject.pipelines.JsonWriterPipeline': 800,
	}

	def __init__(self , keywords=None , topic=None , *args , **kwargs) : 
		super(IeeSpider , self).__init__(*args,**kwargs)
		self.start_urls = ['https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=%s' %keywords]
		self.topic = topic


	def start_requests(self):
		for url in self.start_urls:
			yield SplashRequest(url, self.parse, args={'wait': 2})

	def parse(self, response):
		with open("render.html", "w") as f:
			f.write(str(response._get_body()))
		for article in response.css('a::attr(href)'):
			# for each article go to article details new request get response parse store
			# yield {'title': article.css('a.result-list-title-link').extract_first()}
			if '/document/' in article.extract(): 
				yield SplashRequest('https://ieeexplore.ieee.org' + article.extract(),self.parse_article, args={'wait': 3})
			#
		#for next_page in response.css('a.next::attr("href")'):
		#	yield response.follow(next_page, self.parse)

	def parse_article(self,response) : 
		item = LibscienceItem()
		# response conains the article details page
		title = response.css('.document-title').css('span::text').extract_first() 

		authors = ";".join(response.css('.authors-info').css('span').css('a').css('span::text').extract())

		# affiliation_name = response.css('.affiliation_name::text').extract_first() if response.css('.affiliation_name::text').extract_first() is not None else ""
		# affiliation_city = response.css('.affiliation__city::text').extract_first() if response.css('.affiliation__city::text').extract_first() is not None else ""
		# affiliation_country = response.css('.affiliation__country::text').extract_first() if response.css('.affiliation__country::text').extract_first() is not None else "USA"

		abstract = response.css('.abstract-desktop-div-sections').css('div.abstract-desktop-div').css('div::text').extract()

		location = response.css('.doc-abstract-conferenceLoc::text')
		pub_year = response.css('.doc-abstract-confdate::text')
		if not(pub_year): 
			pub_year = response.css('.stats-document-abstract-publishedIn').css('a::text')
			pub_year = ''.join(pub_year.extract()).split(' ')[0]
		else :
			pub_year = pub_year.re(r'\d{4}')[0]
			

		item['title']= title
		item['authors']= ''.join(authors) 
		item['abstract_']= ''.join(''.join(abstract))
		item['country']= None if not(location) else location.extract_first().split(",")[-1].strip()
		item['date_pub'] =  pub_year
		item['topic'] = self.topic		
		item['latitude'] =  0
		item['longtitude'] = 0
		# item['journal'] = ''.join(''.join(pub_year.extract()).split(' ')[1:])
		yield item
