#!/usr/local/bin/python

import json
import memcache
import requests
import time



'''
for each domain:
    download the new data
    store it in memcache 
        use one obj so its an atomic write
        use new data as current and make old one prev
'''
def fetch_data(config):
    user_agent = {'User-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"}

    for host in config["hosts"]:
        params = {
            "apikey" : config["apikey"],
            "host": host,
            "limit": config["limit"]
        }

        r = requests.get(config["apiurl"], params=params, headers=user_agent)
        print "fetching data for %s..." % (host)
        key = str(host)
        obj = mc.get(key)
        if not obj:
            new_object = {'previous': [], 'current': r.json()}
        else:
            new_object = {'previous': obj['current'], 'current': r.json()}
            #new_object = {'previous': r.json(), 'current': r.json()}
        mc.set(key, new_object)

# start script loop: fetch + sleep
if __name__ == "__main__":
    config = json.load(open('config.json'))
    mc = memcache.Client(['127.0.0.1:11211'])
    while True:
        fetch_data(config)
        time.sleep(5)
