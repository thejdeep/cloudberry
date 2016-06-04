#!/usr/bin/python
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from urllib2 import URLError, urlopen, HTTPError
from urllib import urlencode
from json import loads, dumps
from bottle import route, run, template, static_file, request

import sys
if len(sys.argv)==1:
    asterix_server = "http://localhost:19002"
else:
    asterix_server = sys.argv[1]

# Core Routing
@route('/')
def jsontest():
    return template('tweetbook')

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

# API Helpers
def build_response(endpoint, data):
    api_endpoint = asterix_server + "/" + endpoint

    try:
        # Encode data into url string
        urlresponse = urlopen(api_endpoint + '?' + urlencode(data))

        # There are some weird bits passed in from the Asterix JSON.
        # We will remove them here before we pass the result string
        # back to the frontend.
        urlresult = ""
        CHUNK = 16 * 1024
        while True:
            chunk = urlresponse.read(CHUNK)
            if not chunk: break
            urlresult += chunk
        # Create JSON dump of resulting response
        possibleMultiResults = '[' + urlresult.replace(' ]\n[', ' ],\n[') + ']'

        return dumps(dict(results=loads(possibleMultiResults)))

    except ValueError, e:
        pass

    except URLError, e:

        # Here we report possible errors in request fulfillment.
        if hasattr(e, 'reason'):
            print 'Failed to reach a server.'
            print 'Reason: ', e.reason

        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
        pass
    except Exception:
        pass

# API Endpoints
@route('/query')
def run_asterix_query():
    return (build_response("query", dict(request.query)))

@route('/aql')
def run_asterix_mix_query():
    return (build_response("aql", dict(request.query)))

@route('/query/status')
def run_asterix_query_status():
    return (build_response("query/status", dict(request.query)))

@route('/query/result')
def run_asterix_query_result():
    return (build_response("query/result", dict(request.query)))

@route('/ddl')
def run_asterix_ddl():
    return (build_response("ddl", dict(request.query)))

@route('/update')
def run_asterix_update():
    return (build_response("update", dict(request.query)))

@route('/query/tweet/<id>')
def get_tweet(id):
    url = "https://api.twitter.com/1/statuses/oembed.json?id="+id
    try:
        content = urlopen(url).read()
        return content
    except HTTPError, e:
        pass

run(host='0.0.0.0', port=80, debug=True)