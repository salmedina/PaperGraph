#!/usr/bin/python

import urllib2, os

FreeCiteURL = 'http://freecite.library.brown.edu/citations/create'

def parseRef(txt):
	res = None
	req = urllib2.Request(FreeCiteURL, data=txt ,headers = {'Accept':'text/xml'})

	try:
		res = urllib2.urlopen(req)
		return result.read()
	except urllib2.HTTPError as e:
		error_message = e.read()
		print error_message
	return res