#!/usr/bin/env python3

from http.server import HTTPServer, SimpleHTTPRequestHandler, test

import sys
import os

class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    if len(sys.argv) < 2:
      print("Usage: {} <directory>".format(sys.argv[0]))
      sys.exit(1)

    directory = sys.argv[1]
  
    os.chdir(directory)
    test(CORSRequestHandler, HTTPServer, port=8080)