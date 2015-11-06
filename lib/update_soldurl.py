#! /usr/bin/python

import rp_network
import rp_util
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

client = MongoClient() 

db = client['pyreal']

proxies = db.proxies.find()
soldurls = db.soldurls.find()


for url in soldurls[333:340]:
    html = rp_network.rp_open(url['url'],proxies)
    if html:
        soup = BeautifulSoup(html)
        ele_num = soup.find("div",class_="resultsInfo rui-clearfix")
        print ele_num
    else:
        print 'http failed'


client.close()

