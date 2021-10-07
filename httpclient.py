#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Modifications copyright (C) 2021 Manu Parashar, https://github.com/mparasha
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = int(data[0].split(' ')[1])
        return code

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0].split("\r\n")

    def get_body(self, data):
        return "\r\n\r\n".join(data.split("\r\n\r\n")[1:])
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Parse the url
        urlParsed = urllib.parse.urlparse(url)
        scheme = urlParsed.scheme
        host = urlParsed.hostname
        port = urlParsed.port
        path = urlParsed.path
        
        # if port not provided we take 80 as the default port
        if(port is None):
            port = 80

        # connect to the host
        self.connect(host, port)

        if(len(path) == 0):
            path = '/'
        
        # construct GET request
        request = "GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n".format(path = path, host= host)

        # send the GET request
        self.sendall(request)

        # server response
        response = self.recvall(self.socket)

        # server response headers
        headers = self.get_headers(response)

        # status code
        code = self.get_code(headers)

        # response data
        body = self.get_body(response)

        # close the socket
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # parse the url
        urlParsed = urllib.parse.urlparse(url)
        scheme = urlParsed.scheme
        host = urlParsed.hostname
        port = urlParsed.port
        path = urlParsed.path

        # if port not provided we take 80 as the default port
        if(port is None):
            port = 80

        # connect to the host
        self.connect(host, port)

        if(len(path) == 0):
            path = '/'

        # POST data
        postBody = ""

        if(args is not None):
            postBody = urllib.parse.urlencode(args)
        
        contLen = len(postBody)

        # construct POST request
        request = "POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {contLen}\r\n\r\n{postBody}""".format(path= path, host= host, contLen= contLen, postBody= postBody)

        # send the POST request
        self.sendall(request)

        # server response
        response = self.recvall(self.socket)

        # server response headers
        headers = self.get_headers(response)

        # status code
        code = self.get_code(headers)

        # response data
        body = self.get_body(response)

        # close the socket
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
