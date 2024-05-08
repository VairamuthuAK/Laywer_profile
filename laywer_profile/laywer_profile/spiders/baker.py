import re
import json
import requests
from csv import DictWriter
from parsel import Selector

url = "https://www.bakermckenzie.com/en/api/sitecore/people/getfilters?typeQueryKey=professionals"

payload = {}
headers = {
    "authority": "www.bakermckenzie.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-length": "0",
    "content-type": "application/json; charset=utf-8",
    #   'cookie': 'OptanonAlertBoxClosed=2023-05-03T09:20:48.511Z; nmstat=dd578ee1-925d-1d71-85e5-ef8c8efbda6b; _mkto_trk=id:000-SJL-624&token:_mch-bakermckenzie.com-1683105684890-91167; website#lang=en; shell#lang=en; ASP.NET_SessionId=behyhiyl1dwmuqp5hzjbp0qv; geoIpCurrentRegion=b3875503-8bac-4c09-b959-d37349c9318e; ln_or=eyIyMDQ4MDc2IjoiZCJ9; _gid=GA1.2.1070632474.1683280851; OptanonConsent=isGpcEnabled=0&datestamp=Fri+May+05+2023+16%3A53%3A20+GMT%2B0530+(India+Standard+Time)&version=6.36.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CC0002%3A1%2CC0003%3A1%2CC0005%3A1&geolocation=IN%3BTN&AwaitingReconsent=false; _ga=GA1.1.476664850.1683105649; _ga_QNWJJ7ZFPG=GS1.1.1683280850.4.1.1683286068.0.0.0',
    "origin": "https://www.bakermckenzie.com",
    "referer": "https://www.bakermckenzie.com/en/people/",
    "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

response = requests.request("POST", url, headers=headers, data=payload)
res = json.loads(response.text)
blocks = res[0]["Filter"]
item = {}
for block in blocks:
    personla_link = block["Url"]
    urls = "https://www.bakermckenzie.com" + personla_link
    try:
        req = requests.get(urls, headers=headers)
        blog = Selector(text=req.text)
        '''Method to scrapy field baker site person details'''
        item["site_name"] = "bakermckenzie"
        item["site_url"] = "https://www.bakermckenzie.com/en/people"
        item["source_url"] = urls
        item["name"] = blog.xpath('//h1[@class="name"]/text()').get("")
        item["title"] = blog.xpath('//div[@class="title"]/text()').get("")
        area_of_speciality = blog.xpath('//h3[contains(text(),"Expertise")]/parent::div/ul/li/a/text()').getall()
        item["area_of_speciality"] = "|".join(area_of_speciality)
        email1 = blog.xpath('//li[@class="contact-link"]/a/@data-email').get("")
        email1 = re.sub("\d+", "", email1).replace("+", "").strip()
        email2 = blog.xpath('//li[@class="contact-link"]/a/@data-emaildom').get("")
        email2 = re.sub("\d+", "", email2).replace("+", "").strip()
        if email1 and email2 != "":
            item["email"] = email1 + "@" + email2
        else:
            item["email"] = ""
        number = blog.xpath('//ul[@class="contact-numbers"]/li/a/text()').get("")
        if not "@" in number:
            item["contact_number"] = number
        else:
            item["contact_number"] = ""
        file_names = [
            "site_name",
            "site_url",
            "source_url",
            "name",
            "title",
            "area_of_speciality",
            "email",
            "contact_number",
        ]
        with open("baker2.csv", "a+", encoding="utf-8-sig", newline="\n") as f:
            file_writer = DictWriter(f, fieldnames=file_names)
            file_writer.writerow(item)
            f.close()
    except:
        with open("error.txt", "a") as f:
            f.write(urls + "\n")
