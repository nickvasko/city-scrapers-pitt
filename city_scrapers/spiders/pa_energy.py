from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import datetime


class PaEnergySpider(CityScrapersSpider):
    name = "pa_energy"
    agency = "PA Department of Environmental Protection"
    timezone = "America/New_York"
    allowed_domains = ["www.ahs.dep.pa.gov"]
    start_urls = ["http://www.ahs.dep.pa.gov/CalendarOfEvents/Default.aspx?list=true"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath("//table[contains(@id,'_SingleEventTable')]"):
            self._parse_title_row(item)
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title_row(self, item):
        self.date = item.xpath(".//td[contains(@id,'_titleCell')]/strong/text()").extract()[0].split(' - ')
        self.start_date = self.date[0]
        self.end_date = self.date[0] if len(self.date)==1 else self.date[1]

        title_row = item.xpath(".//td[contains(@id,'_titleCell')]/text()").extract()[0][1:].split(' : ',1)
        self.times = title_row[0].split(' to ')
        self.start_time = self.times[0]
        self.end_time = None if len(self.times)==1 else self.times[1]
        self.title = title_row[1]

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return self.title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return item.xpath(".//td[contains(@id,'descriptionDataCell')]/text()").extract()[0]

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return datetime.datetime.strptime(self.start_date+' '+self.start_time, '%m/%d/%Y %I:%M %p')

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        if self.end_time is None:
            return None
        return datetime.datetime.strptime(self.end_date+' '+self.end_time, '%m/%d/%Y %I:%M %p')

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": item.xpath(".//td[contains(@id,'locationDataCell')]/text()").extract()[0],
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        webaddress = item.xpath(".//td[contains(@id,'webaddressDataCell')]/a/@href").extract()
        if len(webaddress) == 0:
            webaddress = [""]
        return [{"href": webaddress[0],
                 "title": self.title
        }]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
