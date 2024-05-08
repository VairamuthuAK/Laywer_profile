import re
import html
import scrapy


class Rpc(scrapy.Spider):
    name = "rpc"
    start_urls = ["https://www.rpc.co.uk/people/?alltags=true"]

    def parse(self, response):
        """Method to find people link and also who doesn't have link finding details from listing page"""
        for block in response.xpath(
            '//div[@class="team-member stacked"]/div[@class="content"]'
        ):
            people_link = block.xpath('./p//a[@class="more hoverLine"]/@href').get("")
            data_name=block.xpath('.//p/a/@data-name').get('')
            data_domain=block.xpath('.//p/a/@data-domain').get('')
            if data_name and data_domain:
                email=f'{data_name}@{data_domain}'
            if not people_link:
                item = {}
                item["site_name"] = "RPC"
                item["site_url"] = "https://www.rpc.co.uk/"
                item["source_url"] = response.url
                item["name"] = block.xpath("./h2/text()").get("")
                item["title"] = block.xpath("./h3/text()").get("")
                item["area_of_speciality"] = ""
                data_name=block.xpath('.//p/a/@data-name').get('')
                data_domain=block.xpath('.//p/a/@data-domain').get('')
                if data_name and data_domain:
                    item["email"]=f'{data_name}@{data_domain}'
                item["contact_number"] = block.xpath("./p[1]/a/text()").get("").strip()
                
                yield item
            else:
                yield scrapy.Request(
                    response.urljoin(people_link),
                    callback=self.parse_details, cb_kwargs={'email':email},
                    errback=self.handle_error,
                )
        next_page = response.xpath('//li[@class="pagination__next"]/a/@href').get("")
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_details(self, response, email):
        """Method to find all people details"""
        item = {}
        item["site_name"] = "RPC"
        item["site_url"] = "https://www.rpc.co.uk/"
        item["source_url"] = response.url
        item["name"] = (
            html.unescape(response.xpath('//div[@itemprop="name"]/text()').get(""))
            .strip()
            .encode("ascii", "ignore")
            .decode()
        )
        item["title"] = response.xpath('//div[@class="profile-job-title"]/text()').get(
            ""
        )
        item["area_of_speciality"] = "|".join(
            response.xpath('//ul[@class="flowed-list"]/li/a/span/text()').getall()
        )
        item["email"]=email
        
        if re.search('itemprop\="telephone">(.*?)<\/span>', response.text):
            item["contact_number"] = "|".join(
                re.findall('itemprop\="telephone">(.*?)<\/span>', response.text)
            )
        else:
            item["contact_number"] = ""
         
        yield item

    def handle_error(self, failure):
        url = failure.request.url
        with open("failed_urls.txt", "a") as f:
            f.write(url + "\n")
