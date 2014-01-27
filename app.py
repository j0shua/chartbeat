#!/usr/local/bin/python

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import json
import memcache

class TrendingHandler(tornado.web.RequestHandler):
    """ handle GET requests:
        validate 'host' in GET and config
        find in memcache
        check that visitors is increasing
        echo list
    """
    def get(self):
        host = self.get_argument("host", None)
        if not host:
            self.send_error(400)
        
        if host not in config["hosts"]:
            self.send_error(404)

        # find it in memcache and parse
        obj = memcache_client.get(str(host))
        if not obj:
            self.send_error(404)

        current = obj.get('current', None)
        previous = obj.get('previous', {})

        if not current:
            self.send_error(404)
           
        # collect output objects (altho we could just slice up current)
        output = []

        # foreach item in current
        for index, data in enumerate(current):
            # look for item in prev
            item = next((d for i,d in enumerate(previous) if data['path'] in d.values()), None)

            # if it wasn't in prev, current is def more than zero
            if not item:
                output.append(data)
                continue

            # if it was in prev, make sure its gt prev
            if item and data['visitors'] > item['visitors']:
                item['is'] = data['visitors']
                item['was'] = item['visitors']
                output.append(item)

        # we're done; just write out the json representation
        self.write("%s" % (tornado.escape.json_encode(output)))
        self.request.finish()

# routing
application = tornado.web.Application([
    (r"/", TrendingHandler),
    (r"/trending", TrendingHandler)
])

''' main server 'runner'
    load config
    connect to memcache
    setup serever loop
'''
if __name__ == "__main__":
    config = json.load(open('config.json'))
    memcache_client = memcache.Client(['127.0.0.1:11211'])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

