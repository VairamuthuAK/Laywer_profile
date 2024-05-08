import scrapy
import re
class Beachcroft(scrapy.Spider):
    name='dac'
    start_urls=['https://www.dacbeachcroft.com/en/gb/people/']
    
    def parse(self, response):
        """Method to find people link and also who doesn't have link finding details from listing page"""
        for block in response.xpath('//section[@class="team-block"]/div[@class="team-block__content"]'):
            people_link=block.xpath('./h3[@class="team-block__name"]/a/@href').get('')
            if not people_link:
                item={}
                item["site_name"]='DAC Beachcroft'
                item["site_url"]='https://www.dacbeachcroft.com/'
                item["source_url"]=response.url
                item["name"]=block.xpath('./h3[@class="team-block__name"]/text()').get('').strip()
                item["title"]=block.xpath('./span[@class="team-block__position"]/text()').get('')
                item["area_of_speciality"]=''
                email=block.xpath('p[@class="team-block__email"]/a/@href').get('')
                if email:
                    item["email"]=re.sub('mailto:','',email)
                else:
                    item["email"]=''
                item["contact_number"]=block.xpath('./p[@class="team-block__phone"]/text()').get('').strip()
                yield item
            else:
                yield scrapy.Request(response.urljoin(people_link), callback=self.parse_details)

        next_page=response.xpath('//ul[@class="arrow-pagination "]/li[3]/a/@href').get('')
        
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_details(self, response):
        """Method to find all people details"""
        item={}
        item["site_name"]='DAC Beachcroft'
        item["site_url"]='https://www.dacbeachcroft.com/'
        item["source_url"]=response.url
        item["name"]=response.xpath('//div[@class="detail__bio"]//div[@class="detail__intro"]/h1/text()').get('')
        item["title"]=response.xpath('//div[@class="detail__bio"]//div[@class="detail__intro"]/h2/text()').get('')
        area_of_speciality=[area.strip() for area in response.xpath('//section[@class="tagging"]/ul[@class="tagging__tags"]/li//text()').getall()]
        delete_empty = [area_element for area_element in area_of_speciality if area_element.strip()]
        item["area_of_speciality"]='|'.join(delete_empty)
        item["email"]=response.xpath('//p[@class="detail__email"]/a/text()').get('').strip()
        item["contact_number"]=response.xpath('//p[@class="detail__tel"]/a/text()').get('').strip()
        yield item