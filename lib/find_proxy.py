from Queue import Queue, LifoQueue
from threading import Thread
import requests
from bs4 import BeautifulSoup

f = open('proxy.csv','w')
f.write(','.join(['url','country','rating','access time','uptime %','online since','last test','ssl']) + '\n')

max_threads = 3
q = LifoQueue()

for i in range(13):
  q.put('http://www.proxy4free.com/list/webproxy'+ str(i) +'.html')

def downloader(queue,fd):
  while True:
    url = queue.get()
    r = requests.get(url)
    if r.status_code == 200:
      parsed_html = BeautifulSoup(r.content)
      table = parsed_html.body.find('table',attrs={'class':'table table-striped proxy-list'})
      table_body = table.find('tbody')

      rows = table_body.findAll('tr')
      print url + ' was fetched\n'
      for row in rows:
          cols = row.findAll('td')
          cols = [ele.text.strip() for ele in cols]
          fd.write(','.join([x for i,x in enumerate(cols) if (i <> 0 and i <> 2 and i <> 9 )]) + '\n')
    q.task_done()
 
for i in range(max_threads):
  worker = Thread(target=downloader, args=(q,f,))
  worker.setDaemon(True)
  worker.start()


q.join()
f.close()
