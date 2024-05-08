import scrapy

class Anthronygold(scrapy.Spider):
    name = "gold"

    def start_requests(self):
        urls = "https://anthonygold.co.uk/people"
        yield scrapy.Request(urls, callback=self.parse)

    def parse(self, response):
        '''Method to scrapy field value link count & value(area_of_spacatity) text collect '''
        services_number = {}
        for block in response.xpath('//select[@class="select-box"]/option'):
            services = block.xpath("./@value").get("")
            if services:
                services_text = block.xpath("./text()").get("").strip()
                services_number[services] = services_text
        '''Method to scrapy field overall people title & personal link collect'''
        for blocks in response.xpath('//div[@class="people-group"]'):
            title = blocks.xpath(".//h1/text()").get("")
            for block in blocks.xpath(".//ul/li"):
                name_link = block.xpath("./a/@href").get("")
                '''The personal value number collect(area_of_spacatity) & append the "services_number" '''
                data_services = block.xpath("./@data-services").get("").split("-")
                value = []
                for id in data_services:
                    if id:
                        value.append(services_number[id])
                data_text = "|".join(value)
                yield scrapy.Request(
                    name_link,
                    callback=self.personal_details,
                    cb_kwargs={"title": title, "area_of_specialist": data_text},
                )

    def personal_details(self, response, title, area_of_specialist):
        '''Method to scrapy field Anthonygold site person details'''
        item = {}
        item["site_name"] = "Anthony Gold"
        item["site_url"] = "https://anthonygold.co.uk/"
        item["source_url"] = response.url
        item["name"] = (response.xpath('//div[@class="section-wrapper-container page-header-container row"]//h1/text()')
            .get("")
            .replace("\n", "")
            .strip()
        )
        item["title"] = title
        item["area_of_specialist"] = area_of_specialist
        email=response.xpath('//div[@class="person-contact-info text-white"]//h4/a[contains(@href,"mailto:")]/text()').getall()
        item['email']=email
        number=response.xpath('//div[@class="person-contact-info text-white"]//h4/a[contains(@href,"tel:")]/text()').getall()
        item['contact_number']=number
        yield item
