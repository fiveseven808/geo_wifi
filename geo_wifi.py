#!/usr/bin/env python
# -*- coding: utf-8 -*-

# seach geo location from wifi mac address
# 2016-06-20 K.OHWADA

#from selenium import webdriver
import sys
import urllib
import urllib2
import json
import time
import requests
import os

try:
	with open(os.path.expanduser("api.key"), 'r') as f:
		contents = f.read()
except IOError:
	print "api.key not found... Quitting"
	sys.exit()
KEY = contents.split('\r\n') # Try and parse out microsoft created files
if len(KEY) <= 1: # If it doesn't parse out properly
	KEY = contents.split('\n') # Try and parse the "normal" way
KEY = KEY[0]
CMD_CHROMEDRIVER = "/usr/local/bin/chromedriver"

#
# GeoWifi
#
class GeoWifi():

	HEADERS = { 'Content-Type' : 'application/json' }

	def request(self, key, addr1, addr2 ):
		url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + key
		print url
		text = self.buildJson( addr1, addr2 )
		#print text #this is a json
		#res = requests.post(url, json=text) # for some reason this isn't very accurate...
		curlurl = str("curl -H \"Content-Type: application/json\" -H \"Accept: application/json\" -X POST -d '"+str(text)+"' " + str(url))
		print curlurl
		res = os.popen(curlurl).read()
		print res
		#req = urllib2.Request(url, text, self.HEADERS)
		res = json.loads(res)
		print res
		#res = urllib2.urlopen(req)
		body = res
		return self.parseResponse(body)

	def buildJson(self, addr1, addr2):
		obj = {}
		obj[ "wifiAccessPoints" ] = self.buildAddressList(addr1, addr2)
		text = json.dumps(obj)
		return text

	def buildAddressList(self, addr1, addr2):
		list = []
		list.append( self.buildAddress(addr1) )
		list.append( self.buildAddress(addr2) )
		return list

	def buildAddress(self, addr):
		dict = { "macAddress": addr }
		return dict

	def parseResponse(self, res):
		#obj = json.loads(res)
		obj = res
		if obj["location"] is None:
			print res
			return None
		if obj["location"]["lat"] is None:
			print res
			return None
		if obj["location"]["lng"] is None:
			print res
			return None
		if obj["accuracy"] is None:
			accuracy = 0
		else:
			accuracy = obj["accuracy"]
		ret = {}
		ret["lat"] = obj["location"]["lat"]
		ret["lng"] = obj["location"]["lng"]
		ret["accuracy"] = accuracy
		return ret

# class end

def openChrome(lat, lng):
	url = "https://maps.google.com/maps?q=" + str(lat) + "," + str(lng) + "&z=12"
	#driver = webdriver.Chrome( CMD_CHROMEDRIVER )
	#driver.get(url);
	print("This is the URL to visit:")
	print url

# main
args = sys.argv
argc = len(args)
if (len(args) < 3):
	print 'Usage: python %s mac_addr_1 mac_addr_2' % args[0]
	exit()

geo = GeoWifi()
res = geo.request( KEY, args[1], args[2] )
if res is None:
	exit()

print str(res["lat"]) + " " + str(res["lng"]) + " "+ str(res["accuracy"])
openChrome( res["lat"], res["lng"] )
"""
print "Press CTRL+C to quit"
try:
	# endless loop
	while True:
		time.sleep(1)
except KeyboardInterrupt:
	# exit the loop, if key interrupt
	pass
"""
# end
