

import scrapy
from ..items import IndeedCmpProfile

class IndeedCmpProfileSpider(scrapy.Spider):
    name = 'indeed_cmp_profile'
    allowed_urls = ['https://www.indeed.com/']
    start_urls = ['https://www.indeed.com/Best-Places-to-Work?y=2016&cc=US&start=',
    'https://www.indeed.com/Best-Places-to-Work?y=2016&cc=US&start=25']

    def verify(self, content):
        if isinstance(content, list):
            if len(content) > 0:
                content = content[0]
                # convert unicode to str
                return content.encode('ascii','ignore')
            else:
                return "NA"
        else:
            # convert unicode to str
            return content.encode('ascii','ignore')

    def parse(self, response):
        # get all employers on page
        employers = response.xpath('//div[@class="cmp-card-content"]/div')
        for employer in employers:
            # get rank for each employer
            rank = employer.xpath('.//div[@id="cmp-curated"]/div[1]/span/text()').extract()
            # get partial and full urls
            parturl = employer.xpath('.//div[@id="cmp-curated"]/div[1]/a/@href').extract_first()
            fullurl = "https://www.indeed.com" + parturl
            # go to fullurl and keep employer rank
            yield scrapy.Request(fullurl, callback = self.parse_employer,
                meta = {'rank':rank})

    def parse_employer(self, response):
        # populate employer rank
        rank = response.meta['rank']
        rank = self.verify(rank)

        # get employer name
        company = response.xpath('//*[@id="cmp-container"]/div/div[1]/div[1]/header/div[2]/div[3]/div/div/div/div[1]/div[1]/div[2]/div[1]/span/text()').extract()
        company = self.verify(company)

        # get employer overall score
        overall = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "cmp-CompactHeaderCompanyRatings-value", " " ))]/text()').extract() 
        overall = self.verify(overall) 

        # get employer industry
        industry = response.xpath('//*[@id="cmp-container"]/div/div[1]/div[2]/div[3]/div/div/div[2]/div/div[3]/div/div[2]/ul/li/a/text()').extract()
        industry = self.verify(industry)

        # get employer review url
        reviewparturl = response.xpath('//*[@id="cmp-skip-header-desktop"]/div/ul/li[3]/a/@href').extract_first()
        reviewfullurl = "https://www.indeed.com" + reviewparturl

        # populate items
        item = IndeedCmpProfile()
        item['rank'] = rank
        item['company'] = company
        item['overall'] = overall
        item['industry'] = industry

        yield item



