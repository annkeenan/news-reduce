#!/usr/bin/env python2.7
import sys
from lxml import html
import requests
from string import punctuation
import unicodedata
import getopt
import db

# url - url of website being scraped
# headline_paths - a list of xpaths to scrape all the headlines
# link_paths - a list of associated xpaths to scrape all urls to those headlines
# article - a dictionary of headlines mapped to their urls
def scraper(url,headline_paths,link_paths):
    # fetch the website
    page = requests.get(url)
    tree = html.fromstring(page.content)

    headlines = []
    links = []

    # select all linked headers
    for path in headline_paths:
        headlines = headlines + tree.xpath(path)
    for link in link_paths:
        links = links + tree.xpath(link)

    # create a map of headlines to links
    articles = dict()
    for headline,link in zip(headlines,links):
        articles[headline.lower().strip()] = link.lower()

    # return the dictionary
    return articles

# headline - the headline of the article being sanitized
# words - the cleaned and useful words of the headline
def sanitize(headline):
    global common_words
    words = []
    for word in headline.split(' '):
        # ignore unicode characters
        word = word.encode('ascii','ignore')
        # clean off leading and trailing punctuation
        word = word.strip(punctuation)
        # ignore common words
        if word not in db.common_words:
            words.append(word)
    # return a listt of words
    return words

# url - url of website being scraped
# key_words - map of key words to their frequency
def mapper(url):
    headline_paths = db.url_map[url].split(';')[0].split('|')
    url_paths = db.url_map[url].split(';')[1].split('|')
    articles = scraper(url,headline_paths,url_paths)
    # store the key words mapped to a count of the number of times repeated
    key_words = dict()
    # iterate through the headlines
    for headline,url in articles.iteritems():
        words = sanitize(headline)
        for word in words:
            if word in key_words:
                key_words[word] += 1
            else:
                key_words[word] = 1
    return key_words
