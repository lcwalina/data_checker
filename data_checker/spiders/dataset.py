import scrapy
from data_checker.items import Dataset


class DatasetSpider(scrapy.Spider):
    name = "dataset"
    allowed_domains = ["catalog.data.gov"]
    start_urls = ["https://catalog.data.gov/dataset"]
    max_pages = 5

    custom_settings = {
        "FEED_FORMAT": "json",
        "FEED_URI": "file:///tmp/%(name)s/%(time)s.json",
    }

    def parse(self, response):
        base_url = "https://catalog.data.gov"
        for dataset in response.css(".dataset-content"):
            yield Dataset(
                name=dataset.css(".dataset-heading > a::text").get().strip(),
                link=base_url + dataset.css(".dataset-heading > a::attr(href)").get(),
                organization=dataset.css(".dataset-organization::text")
                .get()
                .strip(" —"),
            )

        for link in response.css(".pagination > li:last-child:not(.active) > a"):
            page_number = int(link.attrib["href"].split("=")[1])
            if page_number > self.max_pages:
                break
            yield response.follow(link, callback=self.parse)
