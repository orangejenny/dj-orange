import re
import requests

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand

from orange.models import (
    AGE_DIVISIONS,
    DIVISION_CHOICES,
    ROLE_CHOICES,
    ROUND_CHOICES,
    ColumnScore,
    Competition,
    Event,
    Person,
    RowScore,
)

class Command(BaseCommand):
    BASE_URL = "https://eepro.com/results"
    only_single = False
    only_year = None

    def add_arguments(self, parser):
        parser.add_argument('--single', action='store_true')
        parser.add_argument('--year')

    def clear_data(self):
        Person.objects.all().delete()
        Event.objects.all().delete()
        Competition.objects.all().delete()
        RowScore.objects.all().delete()
        ColumnScore.objects.all().delete()

    def get_soup(self, url):
        req = requests.get(url)
        return BeautifulSoup(req.text, 'html.parser')


    def get_urls(self, year):
        if self.only_single:
            return {"https://eepro.com/results/madjam2023/jjfinals.html"}

        urls = set()
        soup = self.get_soup(f"{self.BASE_URL}/{year}/")
        for a in soup.ul.find_all('a'):
            if 'Jack' in a.text and 'Jill' in a.text:
                href = a.get('href')
                href = href.replace("..", self.BASE_URL)
                urls.add(href)
        return urls

    def process_results(self, url):
        (event, role) = self.parse_url(url)
        print(f"{event} {role} from {url}")

        soup = self.get_soup(url)
        tables = soup.find_all('table')

        for table in tables:
            self.process_table(event, role, table)

    def parse_url(self, url):
        result = re.search(r"/(\w+)/(\w+).html$", url)
        if result is not None:
            (event, page) = result.groups()
        role = None
        for letter, label in ROLE_CHOICES:
            if label.lower() in page.lower():
                role = letter
        return event, role
        

    def process_table(self, event, role, table):
        rows = table.find_all('tr')
        if not rows:
            return
        (division, _round) = self.parse_title(rows[0].td.text.lower())
        if not division:
            return

        comp = Competition(event=event, role=role, division=division, _round=_round)
        comp.save()

        competitor_col = None
        judge_cols = {}
        in_judges = False
        promote_col = None
        for i, cell in enumerate(rows[1].find_all('td')):
            if "competitor" in cell.text.lower():
                competitor_col = i
                in_judges = True
            elif "bib" == cell.text.lower():
                in_judges = False
            elif "promote" in cell.text.lower():
                promote_col = i
            elif in_judges:
                judge_cols[cell.text] = i

        for row in rows[2:]:
            cols = row.find_all('td')
            if comp.role:
                row_scores = [RowScore(competitor=cols[competitor_col].text, competition=comp, promote=bool(cols[promote_col].text))]
            else:
                competitors = cols[competitor_col].text.split(" and ")
                row_scores = [
                    RowScore(competitor=c, competition=comp)
                    for c in competitors
                ]
            for rs in row_scores:
                rs.save()
            for judge, col in judge_cols.items():
                for rs in row_scores:
                    ColumnScore(row_score=rs, judge=judge, score=cols[col].text).save()

    def parse_title(self, title):
        division = None
        for div in AGE_DIVISIONS:
            if div.lower() in title:
                return None, None
        for letter, label in DIVISION_CHOICES:
            if label.lower() in title:
               division = letter 

        _round = None
        for letter, label in ROUND_CHOICES:
            if label.lower() in title:
                _round = letter

        return division, _round

    def handle(self, *args, **options):
        self.only_single = options.get('single')
        self.only_year = int(options.get('year')) if options.get('year') else None

        self.clear_data()
        urls = set()
        years = range(self.only_year, self.only_year + 1) if self.only_year else range(2018, 2024)
        for year in years:
            urls = urls.union(self.get_urls(year))

        for url in urls:
            self.process_results(url)
