#!/usr/bin/env python
# Version: 2.12212017.917

from pymongo import MongoClient
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import StringIO
import argparse
import logging
import sys
import time
import urllib2

logging.basicConfig()
logger = logging.getLogger(__name__)

def f_insert_update_query(in_collection, in_query):
    v_exists = in_collection.find({"query": in_query}).count()

    if v_exists == 1:
        v_doc = in_collection.find({"query": in_query})
        for i in v_doc:
            v_query_count = i["count"]
        print v_query_count
        in_collection.update({"query": in_query}, {"$set": {"count": int(v_query_count+1)}})
    else:
        in_collection.insert({"query": in_query,"count" : 1})

class RevereseProxy(BaseHTTPRequestHandler):
    queries = {}
    mongo_url = "mongodb://next_bus_proxy:asdfgh123@ds123361.mlab.com:23361/next_bus_db_dev"
    mongo_db = "next_bus_db_dev"
    mongo_collection = "next_bus_queries"
    v_client = MongoClient(mongo_url)
    v_collection = v_client[mongo_db][mongo_collection]
    v_delay_collection = v_client[mongo_db]["next_bus_delay_queries"]

    def do_HEAD(self):
        self.do_GET(method='HEAD', body=False)

    def do_GET(self, method='GET', body=True):
        commands = self.path
        if commands[2:] == 'getAPIStats':
            # Expose an API endpoint

            sio = StringIO.StringIO()
            # Fetch and print data from central mongodb database
            # sio.write('====BEGIN STATS=====\n')
            sio.write('\"slow_requests\":{\n\n')
            v_documents = self.v_collection.find({})
            for doc in v_documents:
                v_query = doc["query"]
                v_count = doc["count"]
                v_line = '    \"' + v_query + "\" : \" " + str(v_count) + '\",\n'
                sio.write(v_line)
            sio.write('}\n\n')

            sio.write('\"queries\":\n')
            sio.write('{\n')
            sio.write('\n')
            v_documents = self.v_delay_collection.find({})
            for doc in v_documents:
                v_query = doc["query"]
                v_response_time= doc["response_time"]
                v_line = '    \"' + v_query + "\" : \" " + str(v_response_time) + '\",'
                sio.write(v_line + '\n')
            sio.write('}')
            # sio.write('\n====END STATS=======\n')

            logger.info(sio.getvalue())

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(sio.getvalue())))
            self.end_headers()
            if body:
                self.wfile.write(sio.getvalue())
            return

        else:
            start = time.time()
            try:
                try:
                    url = 'http://webservices.nextbus.com/service/publicXMLFeed'

                    url = url + commands[1:]
                    print(url)
                    req = urllib2.Request(url)

                    try:
                        # retrive_start = time.time()
                        resp = urllib2.urlopen(req)
                        retrive_end = time.time()
                        # retrive_response_time = retrive_end - retrive_start        # Time requried to obtain the response from server

                    except urllib2.HTTPError as e:
                        if e.getcode():
                            resp = e
                        else:
                            self.send_error(599, u'error proxying: {}'.format(unicode(e)))
                            sent = True
                            return

                    self.send_response(resp.getcode())
                    self.end_headers()
                    sent=True
                    self.wfile.write(resp.read())
                finally:
                    if resp:
                        resp.close()
            except IOError as e:
                if not sent:
                    self.send_error(404, 'error trying to proxy: {}'.format(str(e)))
            end = time.time()
            response_time = end - start
            print 'Response time: '+ str(response_time)

            # Store statistics
            store = commands[2:]
            threshold =1 # in seconds
            if store in RevereseProxy.queries:
                RevereseProxy.queries[store] = RevereseProxy.queries[store] + 1
            else:
                RevereseProxy.queries[store] = 1
            # f_insert_update_query(str(store))
            f_insert_update_query(self.v_collection, str(store))
            if response_time >= threshold:
                self.v_delay_collection.insert({"query":str(store),"response_time":response_time})

class EchoHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET(method='HEAD', body=False)

    def do_GET(self, method='GET', body=True):
        try:
            try:
                sio = StringIO.StringIO()
                sio.write('====BEGIN REQUEST=====\n')
                sio.write(self.command)
                sio.write(' ')
                sio.write(self.path)
                sio.write(' ')
                sio.write(self.request_version)
                sio.write('\n')
                for line in self.headers.headers:
                    sio.write(line)
                sio.write('\n')
                # if self.rfile:
                #    sio.write(self.rfile.read())
                sio.write('\n')
                sio.write('====END REQUEST=======\n')
                logger.info(sio.getvalue())

                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', str(len(sio.getvalue())))
                self.end_headers()
                if body:
                    self.wfile.write(sio.getvalue())
                return
            finally:
                sio.close()
        except IOError:
            self.send_error(404, 'file not found')


def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Either HTTP Echo server or ReverseProxy server for nextBus')
    parser.add_argument('--port', dest='port', type=int, default=80,
                        help='serve HTTP requests on specified port (default: 80)')
    parser.add_argument('--type', dest='server_type', choices=['echo','rproxy'], default='rproxy',
                        help='Whether to run as a reverse proxy server or echo server')
    args = parser.parse_args(argv)
    return args


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    print('http server is starting on port {}...'.format(args.port))
    server_address = ('0.0.0.0', args.port)

    if args.server_type == 'echo':
        httpd = HTTPServer(server_address, EchoHTTPRequestHandler)
    else:
        httpd = HTTPServer(server_address, RevereseProxy)
    print('http server is running as {}...'.format(args.server_type))
    httpd.serve_forever()


if __name__ == '__main__':
    main()
