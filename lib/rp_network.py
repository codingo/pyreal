#! /usr/bin/python
import rp_util

import urllib2
from bs4 import BeautifulSoup
import requests


"""
This is the library for network functions
"""

def get_proxy(all_proxies):
    """
    reandomly return a proxy server
    """
    proxies = {}
    random_id = rp_util.get_random_id(all_proxies.count())
    proxies['http'] = all_proxies[random_id]['http']
    return proxies

def get_header():
    """
    randomly return a header for http, use different Agent-Name
    """
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    return header

def get_soup(str_url):
    """
    return a soup object for a given url
    """
    soup = BeautifulSoup(r)
    return soup

def get_sold_page_url(suburb_str,page_num):
    """
    return the url for sold page per suburb
    suburb_str like kellyville+nsw+2155
    """
    return "http://www.realestate.com.au/sold/in-"+suburb_str +"/list-"+str(page_num)+"?includeSurrounding=false"

def get_max_page(int_total_property):
    """
    return the max page based on total property
    """
    per_page = 20
    if int_total_property <= 20:
        return 1
    else:
        return (int_total_property - (int_total_property % per_page)) / per_page + 1

def rp_open(url,all_proxies):
    proxies = get_proxy(all_proxies)
    header = get_header()
    print 'Fetching ' + url
    print 'Using proxy - ' + proxies['http']
    r = requests.get(url,proxies = proxies, headers = header)
    if r.status_code == 200:
        return r.content
    else:
        print r.status_code
        return False
