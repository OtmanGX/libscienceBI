import scrapy
from libscience.items import LibscienceItem
from scrapy_splash import SplashRequest

script="""
function main(splash)
  local url = splash.args.url
  assert(splash:go(url))
  splash:wait(2)
  splash:runjs([[
    document.querySelector('button.show-hide-details.u-font-sans').click();
  ]])
  function wait_for(splash, condition)
	    while not condition() do
	        splash:wait(0.5)
	    end
	end

	wait_for(splash, function()
	    return splash:evaljs("document.querySelector('dl.affiliation dd') != null")
	end)
  return {html = splash:html()}
end
"""

class ScienceDirectSpider(scrapy.Spider):
	name = 'sd'
	topic = "None"
	custom_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
    }
	
	ITEM_PIPELINES = {
		'myproject.pipelines.PricePipeline': 300,
		'myproject.pipelines.JsonWriterPipeline': 800,
	}

	def __init__(self , keywords=None , topic=None , *args , **kwargs) : 
		super(ScienceDirectSpider , self).__init__(*args,**kwargs)
		self.start_urls = ['https://www.sciencedirect.com/search/advanced?qs=%s&zone=qSearch#submit' %keywords]
		self.topic = topic

	def start_requests(self):
		for url in self.start_urls:
			yield SplashRequest(url, self.parse)

	def parse(self, response):
		for index, article in enumerate(response.css('a.result-list-title-link::attr(href)')):
			if '/science/article/' in article.extract(): 
				journal = ''.join(response.css('ol.SubType.hor')[index].css('*::text').getall())
				yield SplashRequest('https://www.sciencedirect.com' + article.extract(),
					lambda res:self.parse_article(res, journal), args={'lua_source': script,'wait':3}, endpoint='execute')
			#
		#for next_page in response.css('a.next::attr("href")'):
		#	yield response.follow(next_page, self.parse)

	def parse_article(self,response, journal) : 
		item = LibscienceItem()
		# response conains the article details page
		title = response.css('h1 .title-text::text').get()

		authors = response.css('.author>.content')
		authors = map(' '.join, (author.css('.text::text').getall() for author in authors))

		abstract = response.css('#abstracts h2.section-title+div>p::text')

		location = response.css('dl.affiliation dd::text')
		location_set = set()
		if location:
			for loc in location.getall():
				location_set.add(loc.split(',')[-1].strip())
		pub_year = response.css('#publication-title+div::text')


		item['title']= title
		item['authors']= ';'.join(authors) 
		item['abstract_']= abstract.get()
		item['country']= ';'.join(loc for loc in location_set)
		item['date_pub'] = pub_year.re(r'\d{4}')[0]
		item['topic'] = self.topic		
		item['latitude'] =  0
		item['longtitude'] = 0
		item['journal'] = journal
		yield item