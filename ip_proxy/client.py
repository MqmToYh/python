#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2

def main():
    response = urllib2.urlopen("http://127.0.0.1:8089", timeout = 10)
    text = response.read()
    print text

if __name__ == '__main__':
    main()
