#! /usr/bin/python
from Queue import Queue, LifoQueue
from threading import Thread
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient



f = open('proxy.csv','w')
f.write(','.join(['url','country','rating','access time','uptime %','online since','last test','ssl']) + '\n')

client = MongoClient() 

db = client['pyreal']
proxies = db.proxies
proxies.remove()
proxy_tmp = {}

max_threads = 3
q = LifoQueue()

start_url = 'http://www.proxy4free.com/list/webproxy1.html'

# get how many pages on the page
r = requests.get(start_url)
if r.status_code == 200:
    soup = BeautifulSoup(r.content)
    ele_page_num = soup.find("ul",class_="content-list-pager")
    ele_pages = ele_page_num.find_all("li")
    num_of_pages = len(ele_pages)
    print 'Total number of pages: ' + str(num_of_pages)
else:
    print 'Get proxy error, start url does not work'

def test_proxy(proxy_dict):
    url = 'http://www.realestate.com.au'
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.101 Chrome/45.0.2454.101 Safari/537.36'}
    r = requests.get(url, proxies = proxy_dict, headers = headers)
    if r.status_code == 200:
        return True
    else:
        return False

for i in range(num_of_pages):
  q.put('http://www.proxy4free.com/list/webproxy'+ str(i+1) +'.html')

def downloader(queue,fd):
  while True:
    url = queue.get()
    r = requests.get(url)
    if r.status_code == 200:
      parsed_html = BeautifulSoup(r.content)
      table = parsed_html.body.find('table',attrs={'class':'table table-striped proxy-list'})
      table_body = table.find('tbody')

      rows = table_body.find_all('tr')
      print url + ' was fetched\n'
      for row in rows:
        proxy_tmp = {}
        ele_td = row.find("td",class_="first nsb")
        proxy_tmp['http'] = 'http://' + ele_td.text + ':80'
        if test_proxy(proxy_tmp):
            proxies.insert(proxy_tmp)
        else:
            print proxy_tmp['http'] + ' does not work, ignore it'
    q.task_done()
 
for i in range(max_threads):
  worker = Thread(target=downloader, args=(q,f,))
  worker.setDaemon(True)
  worker.start()


q.join()
f.close()
client.close()
