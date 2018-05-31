import urllib.request
import json
from html.parser import HTMLParser
import re

class SchoolParser(HTMLParser):
    read = False
    schools = []
    closing_ul_tags = 2

    def handle_starttag(self, tag, attrs):
        if 'ul' == tag and ('class', 'links') in attrs:
            self.read = True
        if self.read and 'a' == tag:
            self.schools.append(attrs[0][1])


    def handle_endtag(self, tag):
        if self.read and 'ul' == tag:
            self.closing_ul_tags -= 1
        if self.read and self.closing_ul_tags <= 0:
            self.read = False


class LunchParser(HTMLParser):
    trash = ('Känner','Menyn saknas', '\n\t\t', 'Hej! Kul', 'STÄNGT', 'Allergener')
    read = False
    lunches = []
    def handle_starttag(self, tag, attrs):
        if 'div' == tag and ('class', 'items') in attrs:
            self.read = True


    def handle_data(self, data):
        if self.read:
            if not data or data.startswith(self.trash) or '\n' in data:
                return
            self.lunches.append(data)


    def handle_endtag(self, tag):
        if self.read and 'div' == tag:
            self.read = False


def get_counties():
    req = urllib.request.Request("https://skolmaten.se/")
    with urllib.request.urlopen(req) as request:
        for line in request.read().decode('utf-8').split():
            if line.startswith('href="/p/'):
                yield line.split('"')[1]


def get_district(lan):
    req = urllib.request.Request("https://skolmaten.se/"+lan)
    with urllib.request.urlopen(req) as request:
        for line in request.read().decode('utf-8').split():
            if line.startswith('href="/d/'):
                yield line.split('"')[1]


def get_schools(district):
    req = urllib.request.Request("https://skolmaten.se/"+district)
    parser = SchoolParser()
    with urllib.request.urlopen(req) as request:
        parser.feed(request.read().decode('utf-8'))

    for school in parser.schools:
        yield school


def get_lunch(school):
    req = urllib.request.Request("https://skolmaten.se/"+school)
    parser = LunchParser()
    with urllib.request.urlopen(req) as request:
        parser.feed(request.read().decode('utf-8'))

    for lunch in parser.lunches:
        yield lunch


def vegetarian_lunch(lunch):
    meats = ['kött','fisk','kyckling','fläsk','kotlett','lamm','pannbiff','kassler', 'sej', 'falukorv', 'skinka', 'skink', 'torsk', 'hoki']
    for meat in meats:
        if meat in lunch.lower():
            return False
    return True


if __name__ == '__main__':
    print("Fetching all lunches from https://skolmaten.se/")
    with open('lunches.txt', 'a') as f:
        for county in get_counties():
            print("Getting from schools in county: {}".format(county[3:-1]))
            for district in get_district(county):
                print("\tDistrict: {}".format(district[3:-1]))
                for school in get_schools(district):
                    print("\t\tSchool: {}".format(school[1:-1]))
                    f.write('\n')
                    for lunch in get_lunch(school):
                        if vegetarian_lunch(lunch):
                            f.write(lunch + '\n')
    print("Done, results are found in 'lunches.txt'")
