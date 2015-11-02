#! /usr/bin/python
import urllib2
from bs4 import BeautifulSoup


"""
This is the library for network functions
"""

def get_proxy():
    """
    reandomly return a proxy server
    """
    url = ''
    return url

def get_header():
    """
    randomly return a header for http, use different Agent-Name
    """
    header = {}
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
