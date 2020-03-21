import random
import sys
from HTMLParser import HTMLParser

import requests
from requests import ConnectionError

rootUrl = 'https://coned.georgebrown.ca'
catalogs = ['https://coned.georgebrown.ca/courses-and-certificates/subject/culinary-arts/',
            'https://coned.georgebrown.ca/courses-and-certificates/subject/baking-arts/',
            'https://coned.georgebrown.ca/courses-and-certificates/subject/food-and-beverage/']


def getHeaders():
    return {
        'Connection': 'close',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{0}_0) '
                      'AppleWebKit/{1}.{2} (KHTML, like Gecko) '
                      'Chrome/75.0.{3}.{4} Safari/{1}.{2}'.format(random.randint(10, 15),
                                                                  random.randint(530, 540),
                                                                  random.randint(30, 40),
                                                                  random.randint(3000, 4000),
                                                                  random.randint(140, 150))
    }


def getDoc(url):
    r = None
    with requests.Session() as sess:
        try:
            sess.keep_alive = False
            r = sess.get(url, headers=getHeaders()).text
        except ConnectionError as e:
            print >> sys.stderr, e
    return r


class CourseListParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.catalog = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            title = None
            url = None
            for a in attrs:
                if a[0] == 'title':
                    title = a[1]
                elif a[0] == 'href' and 'courses-and-certificates' in a[1]:
                    url = rootUrl + a[1]
            if url:
                self.catalog[title] = url


class Schedule(object):

    def __init__(self):
        self.date = None
        self.days = None
        self.time = None

    def __repr__(self):
        return '{}, {}, {}'.format(self.date, self.days, self.time)


class ScheduleParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.schedules = []
        self.ex = None

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            for a in attrs:
                if a[0] == 'data-th':
                    if a[1] == 'Date(s)':
                        self.ex = 'date'
                        self.schedules.append(Schedule())
                    elif a[1] == 'Day(s)':
                        self.ex = 'days'
                    elif a[1] == 'Time':
                        self.ex = 'time'

    def handle_data(self, data):
        if self.ex:
            setattr(self.schedules[-1], self.ex, data.encode('utf-8'))
            self.ex = None


with open('schedule.csv', 'w') as f:
    for catalog in catalogs:
        catalogParser = CourseListParser()
        doc = getDoc(catalog)
        catalogParser.feed(doc)
        for k, v in catalogParser.catalog.items():
            try:
                scheduleParser = ScheduleParser()
                doc = getDoc(v)
                scheduleParser.feed(doc)
                for s in scheduleParser.schedules:
                    print k, ',', s
                    print >> f, k, ',', s
            except:
                print >> sys.stderr, 'skipped:', k
