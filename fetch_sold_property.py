#! /usr/bin/env python

import requests
from bs4 import BeautifulSoup
from Queue import Queue
from threading import Thread
from pymongo import MongoClient
from lib import rp_util
import time


def get_address(property_id):
    base_url = "http://www.realestate.com.au/"
    addr = []
    try:
        r = requests.get(base_url + property_id)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text)
            e_header = soup.find("div",attrs={"id":"listing_header"})
            if e_header:
                h1_addr = e_header.find("h1")
                if h1_addr:
                    for part in h1_addr.find_all("span"):
                        addr.append(part.text)
                else:
                    print 'h1_addr not found'
            else:
                print 'e_header not found'
        else:
            print 'status code wrong'
    except Exception as inst:
        print inst
        return None
    return ",".join(addr)

def fetch_soldproperties(i, q, coll):
    """
    i - the thread id
    soldurl_queue - the queue for start url of sold property
    coll_soldlisturl - MongoDB collection object for sold
    """
    headers = {'User-Agent':'Chrome 4.5'}
    # proxies = {'http':'http://218.200.66.200:8080'}
    while True:
        url = q.get()
        suburb = url.replace('http://www.realestate.com.au/sold/in-','').replace('?activeSort=solddate&includeSurrounding=false','').upper().split('/')[0]
        print 'Thread %s : processing %s' % (i, url)
        # do more work
        try:
            r = requests.get(url, headers = headers)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content)
                result = soup.find("div",attrs = {"id":"searchResultsTbl"})
                if result:
                    properties = result.find_all("article")
                    for p in properties:
                        tmp_dict = {}
                        e1 = p.find("div",class_="listingInfo rui-clearfix")
                        e_price = e1.find("p",class_="priceText")
                        e_sold_date = e1.find("p",class_="soldDate")


                # not found result
                else:
                    print 'Thread %s: %s - no properity found' % (i, suburb)
            else:
                print 'Thread %s: %s - Wrong http code is %s' % (i, suburb, r.status_code)
        except Exception as inst:
            print inst
        # sleep to avoid being blocked
        # sleep for 0.5 second
        print 'Thread %s: sleep for 0.2s' % i
        time.sleep(20)
        q.task_done()



if __name__ == '__main__':
    # set constant variables
    max_threads = 10
    url_q = Queue()
    client = MongoClient()
    db = client['pyreal']
    coll_soldproperties = db.soldproperties


    # prepare the queue
    for item in db.soldlisturls.find().limit(100):
        url_q.put(item['url'])

    for i in range(max_threads):
        worker = Thread(target=fetch_soldproperties, args=(i, url_q, coll_soldlisturls,))
        worker.setDaemon(True)
        worker.start()
    print '*** Main program is waiting ***'
    url_q.join()
    print '*** all done, closing MongoDB connection ***'
    client.close()
