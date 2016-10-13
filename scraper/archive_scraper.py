import scrapy
import requests
from datetime import datetime

# archive_scraper.py: Index historical FiveThirtyEight posts from the archive.org wayback machine
#
# usage: `scrapy runspider scraper/archive_scraper.py -o events.json`
#
# (c) 2016 Matt Meshulam


# Stop after indexing this many pages
PAGE_LIMIT = 50

class ArchiveSpider(scrapy.Spider):
    name = "fivethirtyeight-archive"
    allowed_domains = ['web.archive.org']

    page_count = 0

    start_urls = [
        'https://web.archive.org/web/20090205221829/http://www.fivethirtyeight.com/2008/10/todays-polls-1016.html'
    ]

    def parse_article(self, response):
        timeStr = response.css('span.post-timestamp a::text').extract_first()
        dateStr = response.css('h2.date-header::text').extract_first()
        date = dateStr + ' ' + timeStr
        try:
            date = datetime.strptime(date, '%A, %B %d, %Y %I:%M %p')
            date = date.isoformat()
        except RuntimeError as e:
            print("Got an error:")
            print(repr(e))

        author = response.css('span.post-author::text').extract_first()
        author = author.strip('\n -')

        newurl = ""
        try:
            newurl = response.url[response.url.find('fivethirtyeight.com'):]
            r = requests.get('http://' + newurl)
            newurl = r.url
        except:
            raise

        return {
            'timestamp': date,
            'url': response.url,
            'title': response.css('.post-title a::text').extract_first(),
            'author': author,
            'newurl': newurl,
        }

    def parse(self, response):
        prev_revision = response.css('div#wm-ipp-inside td.b a::attr("href")').extract_first()
        if prev_revision:
            # Don't index this page, go to the earlier revision
            prev_revision = response.urljoin(prev_revision)
            yield scrapy.Request(prev_revision, callback=self.parse)
        else:
            yield self.parse_article(response)

            self.page_count += 1

            next_page = response.css('a.blog-pager-newer-link::attr("href")').extract_first()
            if next_page and self.page_count < PAGE_LIMIT:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)
