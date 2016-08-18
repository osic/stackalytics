#!/usr/bin/env python3

from urllib import request, parse
import json, sys

# Base URL being accessed
url = 'http://stackalytics.com/api/1.0/stats/engineers'

for company in {'Intel','Rackspace'}:

    # Dictionary of query parameters (if any)
    parms = {
        'company': company,
    }

    # Encode the query string
    querystring = parse.urlencode(parms)

    # Make a GET request and read the response
    u = request.urlopen(url+'?' + querystring)
    resp = json.loads(u.read().decode(encoding='UTF-8'))
    statlist=resp['stats']

    for stat in statlist:
        sys.stdout.write(stat['id']+',"'+stat['name']+'"\n')


