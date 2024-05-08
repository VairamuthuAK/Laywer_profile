import scrapy
import re
import urllib.parse
class Osborne(scrapy.Spider):
    name='osborne'
    start_urls=['https://www.osborneclarke.com/lawyers']

    def parse(self, response):
        """Method to find all people_link and pagination_link"""
        for block in response.xpath('//div[@class="MO11__bio"]'):
            people_link=response.urljoin(block.xpath('./a/@href').get(''))
            yield scrapy.Request(people_link, callback=self.parse_details)

        next_page=response.xpath('//li[@class="MO2__next pager__item pager__item--next"]/a/@href').get('')
        
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
            
    def parse_details(self, response):
        """Method to find all people details"""
        item={}
        item["site_name"]='Osborne Clarke'
        item["site_url"]='https://www.osborneclarke.com/'
        item["source_url"]=response.url
        item["name"]=response.xpath('//div[@class="gr OR3__inner"]/div[contains(@class, "OR3__content")]/h1/text()').get('')
        item["title"]=response.xpath('//div[@class="OR3__inner-wrapper font-lubalin"]/span/text()').get('')
        sector='|'.join([sector_element.strip() for sector_element in response.xpath('//div[@class="MO37__section"][1]//li/a/text()').getall()])
        service='|'.join([service_element.strip() for service_element in response.xpath('//div[@class="MO37__section"][2]//li/a/text()').getall()])
        if sector and service:
            item["area_of_speciality"]=[{"Sector":sector}, {"Service":service}]
        elif sector and not service:
            item["area_of_speciality"]=[{"Sector":sector}]
        elif not sector and service:
            item["area_of_speciality"]=[{"Service":service}]
        else:
            item["area_of_speciality"]=''
        
        old_email=response.xpath('//span[@class="OR3__contact__item light icon--email"]/a/@href').get('')
        email=re.sub('mailto:','',urllib.parse.unquote(old_email))
        item["email"]=''
        
        old_contact=[contact_element.strip() for contact_element in response.xpath('//div[@class="OR3__contact"]/a/text()').getall()]
        delete_empty = [old_con_element for old_con_element in old_contact if old_con_element.strip()]
        contact='|'.join(delete_empty)
        item["contact_number"]=''
        

        if "@" in contact:
            item["email"] = contact
        else:
            item["contact_number"] = contact

        if re.search(r'^(\+\d+)?\d+(?<!@)$', email):
            item["contact_number"] = email
        else:
            item["email"] = email
        
        yield item
