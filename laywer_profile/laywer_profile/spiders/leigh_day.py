import scrapy

class LeiSpider(scrapy.Spider):
    name = "leigh_day"
    start_urls = ["https://www.leighday.co.uk/about-us/our-people/"]

    def parse(self, response):

        """Method to find the Leigh day site lawyer's content navigation link"""
        
        for navigation in response.xpath('//div[@class="s-signposting__signposts"]//a'):
            navigation_link = response.urljoin(navigation.xpath("./@href").get(""))
            yield scrapy.Request(navigation_link, callback=self.parse_details)


    def parse_details(self, response):

        """Method to find the lawyer's container, content and next page links"""
        
        for container in response.xpath(
            '//div[@class="b-card"]//div[@class="cta-text-link-chevron"]'
        ):
            content_links = response.urljoin(container.xpath("./p/a/@href").get(""))
            yield scrapy.Request(content_links, callback=self.details)

        next_page = response.xpath('//a[@class="b-pagination__btn-next"]/@href').get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page), callback=self.parse_details
            )


    def person_details(self, response):

        """Method to scraping  all persons details"""     
        
        item = {}
        item["site_name"] = "Leigh Day"
        item["site_url"] = "https://www.leighday.co.uk/"
        item["source_url"] = response.url
        name = response.xpath("//h1/text()").get("").strip()
        title = (

            response.xpath(
                '//p[@class="s-hero-profile-card-item-info__role"]/text()'
            )
            .get("")
            .strip()
        )
        if "|" in name:
            name = name.split("|")[0].strip()
            title = name.split("|")[-1].strip()
        item["name"] = name
        item["title"] = title
        item["area_of_speciality"] = "|".join(
            response.xpath(
                '//div[@class="s-hero-profile-card-item-info__tags"]/span/text()'
            ).getall()
        )
        email = response.xpath(
            '//div[@class="s-hero-profile-card-item s-hero-profile-item-contact"]/p[1]/a/@href'
        ).get("")
        contact_number = response.xpath(
            '//div[@class="s-hero-profile-card-item s-hero-profile-item-contact"]/p[2]/a/@href'
        ).get("")
        
        if "tel:" in email:
            item["email"] = ""
            item["contact_number"] = email.replace("tel:", '')
            
        else:
            item["email"] = email.replace("mailto:", '')
            item["contact_number"] = contact_number.replace("tel:", '')

        yield item

        