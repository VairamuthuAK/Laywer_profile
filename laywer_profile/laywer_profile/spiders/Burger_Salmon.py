import scrapy
import re

def clean_string(data):

    """Method to replacing the unwanted characters"""

    cleaned_data = data.replace("\t", "").replace("\n", " ")
    cleaned_data = data.replace("\\r\\n", "")
    cleaned_data = re.sub(r"\s+", " ", str(cleaned_data))
    return cleaned_data.strip()

class BurSalSpider(scrapy.Spider):

    name = "burger_salmon"
    start_urls = ["https://www.burges-salmon.com/our-people"]

    def parse(self, response):

        """Method to scraping the Burger Salmon site lawyer's container, content and next page links"""       
        
        for container in response.xpath('//div[@class="profile-card__content-container"]'):
            contains_link = container.xpath('.//a[contains(text(),"View profile")]/@href').get()
            yield scrapy.Request(contains_link, callback=self.parse_details)

        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_details(self, response):

        """Method to scraping the Burger Salmon site's all persons details"""

        item = {}
        item["site_name"] = "Burges Salmon"
        item["site_url"] = response.url
        item["name"] = (clean_string(
            response.xpath('//h1/text()')
            .get(""))
        )
        title = response.xpath(
            '//span[@class="personal-profile-header__position"]/text()').get("")
        item["title"] = clean_string(title)        
        item["area_of_speciality"] = "|".join(
            response.xpath("//h3/following-sibling::ul/li/a/text()").getall()
        ).strip()        
        email = response.xpath('//a[@id="phmain_0_emailLink"]/@href').get("")
        item["email"] = email.replace("mailto:", '')

        phone_list = []        
        phone_number = response.xpath('//a[@id="phmain_0_telLink"]/text()').getall()        
        if phone_number != []:
            phone_list.append(phone_number[-1].strip())
        mobile_number = response.xpath('//a[@id="phmain_0_mobileLink"]/text()').getall()
        if mobile_number != []:
            phone_list.append(mobile_number[-1].strip())
        item["contact_number"] = "|".join(phone_list)
        
        yield item
