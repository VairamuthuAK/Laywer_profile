import re
import scrapy

class Bristowspeople(scrapy.Spider):
    name = "people"

    def start_requests(self):
        urls = "https://www.bristows.com/people/"
        yield scrapy.Request(urls, callback=self.parse)

    def parse(self, response):
        '''Method to scrapy field overall link count & overall person link collect '''
        for block in response.xpath('//div[@class="posts boxes"]//a'):
            name_link = block.xpath("./@href").get("")
            '''overall person this field was stander so replace this field'''
            area = (block.xpath("./@class").get("")
                .replace("info-box filter-our_people type2 blue-color ", ""))
            area_list = area.split(" ")
            area_list_clean = [re.sub(r"filter\-[^>]*?\-", "", clean) for clean in area_list]
            area_of_spalitity = "|".join(area_list_clean)
            if name_link != "":
                yield scrapy.Request(
                    response.urljoin(name_link),
                    callback=self.people_details,
                    cb_kwargs={"area_of_spalitity": area_of_spalitity},
                )

    def people_details(self, response, area_of_spalitity):
        '''Method to scrapy field Bristowspeople site person details'''
        item = {}
        item["site_Name"] = "bristows.com"
        item["site_URL"] = "https://www.bristows.com"
        item["source_url"] = response.url
        item["name"] = response.xpath('//h1[@class="text-success"]/text()').get("")
        item["title"] = response.xpath('//h3[@class="text-success"]/text()').get("")
        email=response.xpath('//ul[@class="person-info-list"]/li/a[contains(@href,"mailto")]/text()').get('')
        item['email']=email
        number=response.xpath('//ul[@class="person-info-list"]/li/a[contains(@href,"tel:")]/text()').getall()
        if len(number) > 1:
            item["contact_number"] = number[1].replace("tel:", "")
        else:
            item["contact_number"] = number
        item["area_of_speciality"] = area_of_spalitity
        yield item