#!/usr/bin/env python
import urllib2

commands = [ 'command=agencyList',
             'command=routeList&a=umd',
             'command=routeList&a=sf-muni',
             'command=routeConfig&a=umd&r=118',
             'command=schedule&a=sf-muni&r=N',
             'command=predictionsForMultiStops&a=sf-muni&stops=N|6997&stops=N|3909',
             'command=schedule&a=sf-muni&r=L',
             'command=schedule&a=sf-muni&r=J',

]

for c in commands:
    url = 'http://54.208.29.7'    #Change this IP to HOST IP running the container
    url = url + '?'+ c
    print url
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)
    print str(resp.read())
