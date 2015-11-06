from pymongo import MongoClient
import requests
import sys



def test_proxy(proxy_dict):
    url = 'http://rp.ozdata.info/proxy.html'
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.101 Chrome/45.0.2454.101 Safari/537.36'}
    try:
        r = requests.get(url, proxies = proxy_dict, headers = headers)
        if r.status_code == 200 and r.text.rstrip() == 'Success':
            return True
        else:
            return False
    except Exception as inst:
        print 'Exception for ' + proxy_dict['http']
        return False


if __name__ == '__main__':
    client = MongoClient() 

    db = client['pyreal']
    proxies = db.proxies
    proxies.remove()
    proxy_tmp = {}

    if len(sys.argv) <> 2:
        print 'Please give the csv file name'
        exit(1)
    else:
        filename = sys.argv[1]
        data = [x.rstrip().split('|') for x in open(filename)]
        for item in data:
            proxy_tmp = {}
            proxy_tmp['http'] = 'http://' + item[0] + ':' + item[1]
            if test_proxy(proxy_tmp):
                # verfied
                proxies.insert(proxy_tmp)
                print proxy_tmp['http'] + ' is inserted'
            else:
                print proxy_tmp['http'] + 'does not work'







