from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep
import numpy as np
from unidecode import unidecode
from datetime import datetime
from HTMLParser import HTMLParser
import re

class BestOfMC(object):
    '''
    A class to scrape Best-Of-Craigslist's Missed Connections
    '''
    def __init__(self):
        self.starturl = 'http://www.craigslist.org/about/best/all/mis/'
        self.record_dt = None
        self.df = pd.DataFrame(columns=['title', 'category', 'post_dt', 'post',
                    'loc', 'url', 'record_dt', 'city', 'raw_page', 'has_pic'])
        self._hrefs = []
        self._cities = []

    def get_df(self):
        '''
        Populates self.df with Missed Connection post info
        '''
        self.record_dt = datetime.now()
        soup = self._look_at_page(self.starturl)

        # Get post links (and 'next' link if it exists)
        hrefs, cities = self._get_hrefs_and_cities(soup)
        self._hrefs.extend(hrefs)
        self._cities.extend(cities)
        nextlink = soup.find('a', {'class': 'button next'})['href']

        while len(nextlink) != 0:
            nexturl = 'http:' + str(nextlink)
            nextsoup = self._look_at_page(nexturl)
            nextlink = nextsoup.find('a', {'class': 'button next'})['href']
            hrefs, cities = self._get_hrefs_and_cities(nextsoup)
            self._hrefs.extend(hrefs)
            self._cities.extend(cities)

        # Only keep distinct hrefs while preserving order
        lst = set()
        inds = [i for i in xrange(len(self._hrefs)) if str(self._hrefs[i]) not in lst and not lst.add(str(self._hrefs[i]))]
        self._hrefs = [self._hrefs[i] for i in inds]
        self._cities = [self._cities[i] for i in inds]

        # Populate df with post info
        for url in self._hrefs:
            soup = self._look_at_page(url)
            if soup.find('div', {'class': 'removed'}): # Skip "removed" posts
                continue
            self._get_info(url)
            sleep(1 + 3*np.random.random()) # Avoid getting kicked off server

    def _get_info(self, url):
        soup = self._look_at_page(url)
        raw_page = requests.get(url).content
        title, category = self._get_title_and_cat(soup)
        dt = self._get_datetime(soup)
        post, location = self._get_post_and_loc(soup)
        has_pic = self._has_pic(soup)
        ind = self._hrefs.index(url)
        city = self._cities[ind]

        d = {'title': title, 'category': category, 'post_dt': dt, 'post': post,
            'loc': location, 'url': url, 'record_dt': self.record_dt, 'city': city,
            'raw_page': raw_page, 'has_pic': has_pic}

        if post.startswith('<img'): #don't append posts that only contain images
            return
        self.df = self.df.append(d, ignore_index=True)

    def _get_title_and_cat(self, soup):
        # len('best of craigslist: ') = 20
        temp = unidecode(soup.title.string[20:]).split()
        if temp[-1] in ['m4m', 'm4w', 'w4m', 'w4w']:
            category = temp.pop()
            title = ' '.join(temp[:-1])
        else:
            category = None
            title = unidecode(soup.title.string[20:])
        return title, category

    def _get_datetime(self, soup):
        datetime_text = soup.find('span', {'class': 'greytext'}).text
        # len('Originally Posted: ') = 19
        datetime = datetime_text[19:]
        dt = pd.to_datetime(datetime)
        return dt

    def _get_post_and_loc(self, soup):
        text = []
        location = None
        contents = soup.find(id='postingbody').contents
        for item in contents:
            str_item = unidecode(item)
            if '<li>' in str_item:
                if 'Location: ' in unidecode(item.li.text):
                    # len(' Location: ') = 11
                    if '\n' in unidecode(item.li.text):
                        end_ind = unidecode(item.li.text).index('\n')
                        loc_text = unidecode(item.li.text)[11:end_ind]
                    else:
                        loc_text = unidecode(item.li.text)[11:]
                    location = loc_text.replace('\r', '')
            str_item = html_to_text(str_item)
            text.extend(str_item.strip().split())
        post = ' '.join(text)
        phrases = [" it's NOT ok to contact this poster with services or other commercial interests",
            " It\'s NOT ok to contact this poster with services or other commercial interests"]
        for phrase in phrases:
            post.replace(phrase, '')
        post.replace('[?]', '', 200) # gets rid of emoji placeholders
        phrases2 = [' Location:', ' <!--', ' Other ways to contact poster', ' START CLTAGS']
        for phrase in phrases2:
            if phrase in post:
                end_ind = post.index(phrase)
                post = post[:end_ind]

        return post, location

    def _get_hrefs_and_cities(self, soup):
        trs = soup.findAll('tr')[1:]
        hrefs = []
        cities = []
        for tr in trs:
            hrefs.append(unidecode(tr.a['href']))
            city_start_ind = unidecode(tr.text).index('missed connections')
            # len('missed connections') = 18
            city_text = unidecode(tr.text)[(18 + city_start_ind):].lower()
            if ',' in city_text:
                comma_ind = city_text.index(',')
                city_text = city_text[:comma_ind]
            cities.append(city_text.replace(' ', ''))
        return hrefs, cities

    def _has_pic(self, soup):
        if soup.findAll('figure'):
            return 1
        return 0

    def _look_at_page(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        return soup

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = [ ]

    def handle_data(self, d):
        self.result.append(d)

    def handle_charref(self, number):
        codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
        self.result.append(unichr(codepoint))

    def handle_entityref(self, name):
        self.result.append('&%s;' % name)

    def get_text(self):
        return u''.join(self.result)

def html_to_text(html):
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()
