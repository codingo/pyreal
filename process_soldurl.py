#! /usr/bin/env python

import requests
from bs4 import BeautifulSoup
from Queue import Queue
from threading import Thread
from pymongo import MongoClient
from lib import rp_util
import time

def process_soldurl(i, q, coll_soldlisturl):
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
                result = soup.find("div",class_="resultsInfo rui-clearfix")
                if result:
                    result_str = result.p.text
                    total_num = rp_util.get_total_num(result_str)
                    max_page = rp_util.get_max_page(total_num)
                    print 'Thread %s : %s - total_num/max_page %s/%s' % (i, suburb, total_num, max_page)
                    for page_num in range(1,max_page+1):
                        tmp_dict = {}
                        tmp_dict['url'] = rp_util.replace_page_num(url,page_num)
                        coll_soldlisturl.insert(tmp_dict)
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
    coll_soldlisturls = db.soldlisturls


    # prepare the queue
    for item in db.soldurls.find():
        url_q.put(item['url'])

    for i in range(max_threads):
        worker = Thread(target=process_soldurl, args=(i, url_q, coll_soldlisturls,))
        worker.setDaemon(True)
        worker.start()
    print '*** Main program is waiting ***'
    url_q.join()
    print '*** all done, closing MongoDB connection ***'
    client.close()
