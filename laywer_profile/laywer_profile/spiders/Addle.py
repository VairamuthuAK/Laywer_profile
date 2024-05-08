import re
import scrapy


class Addle_Shaw(scrapy.Spider):
    name = "addle"
    start_urls = ["https://www.addleshawgoddard.com/en/our-people/"]

    def parse(self, response):
        """Method to find all people_link and pagination_link"""
        for block in response.xpath('//div[@class="people-profile__content"]'):
            people_link = response.urljoin(block.xpath("./a/@href").get(""))
            yield scrapy.Request(people_link, callback=self.parse_details)

        next_page = response.xpath(
            '//a[@class="pagination__link btn-round btn-round--next"]/@href'
        ).get("")

        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_details(self, response):
        """Method to scrap all people details"""
        item = {}
        item["site_name"] = "Addleshaw Goddard"
        item["site_url"] = "https://www.addleshawgoddard.com/en/"
        item["source_url"] = response.url
        item["name"] = response.xpath(
            '//div[contains(@class, "col-sm-8")]/h1/text()'
        ).get()
        item["title"] = re.sub(
            r"\s+",
            " ",
            response.xpath(
                '//div[contains(@class, "col-sm-8 banner")]/ul/li/text()'
            ).get(""),
        )
        item["area_of_speciality"] = "|".join(
            response.xpath('//ul[@class="related-links"]/li/a/text()').getall()
        )

        if re.search('<a\s*href\="mailto\:(.*?)">', response.text):
            email = re.findall('<a\s*href\="mailto\:(.*?)">', response.text)[0]
        else:
            email = ""
        item["email"] = ""

        contact = "|".join(
            [
                x.strip()
                for x in response.xpath(
                    '//li[@class="people-profile__contact--tel"]/a/text()'
                ).getall()
            ]
        )

        item["contact_number"] = ""
        if "@" in contact:
            item["email"] = contact
        else:
            item["contact_number"] = contact

        if re.search(r"^(\+\d+)?\d+(?<!@)$", email):
            item["contact_number"] = email
        else:
            item["email"] = email

        yield item
