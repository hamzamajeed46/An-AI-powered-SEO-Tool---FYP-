import scrapy
import pandas as pd
from urllib.parse import urljoin
import os

class BacklinkSpider(scrapy.Spider):
    name = "backlink_spider"

    def start_requests(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_path, "urls.csv")

        df = pd.read_csv(csv_path)
        for url in df['url']:
            yield scrapy.Request(url=url.strip(), callback=self.parse)

    def parse(self, response):
        for link in response.css('a'):
            href = link.attrib.get('href')
            if not href:
                continue

            absolute_url = urljoin(response.url, href)
            anchor_text = link.css('::text').get(default='').strip()
            rel_attr = link.attrib.get('rel', '').split()
            context = link.xpath('string(ancestor::*[self::p or self::div][1])').get(default='').strip()

            yield {
                'source_url': response.url,
                'anchor_text': anchor_text,
                'link_url': absolute_url,
                'rel': " ".join(rel_attr),
                'nofollow': 'nofollow' in rel_attr,
                'context': context
            }
