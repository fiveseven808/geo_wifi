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

#
# GeoWifi
#
class GeoWifi():

    HEADERS = { 'Content-Type' : 'application/json' }

    def request(self, key, addr1, addr2 ):
        url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + key
        #print url
        text = self.buildJson( addr1, addr2 )
        #print text #this is a json
        #res = requests.post(url, json=text) # for some reason this isn't very accurate...
        curlurl = str("curl -H \"Content-Type: application/json\" -H \"Accept: application/json\" -X POST -d '"+str(text)+"' " + str(url))
        #print curlurl
        res = os.popen(curlurl).read()
        print res
        #req = urllib2.Request(url, text, self.HEADERS)
        #res = urllib2.urlopen(req)
        res = json.loads(res)
        print res
        body = res
        return self.parseResponse(body)

    def request_new(self, key, mac_array, p_array ):
        url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + key
        #print url
        text = self.buildJson_array(mac_array, p_array)
        #print text #this is a json
        #res = requests.post(url, json=text) # for some reason this isn't very accurate...
        curlurl = str("curl -H \"Content-Type: application/json\" -H \"Accept: application/json\" -X POST -d '"+str(text)+"' " + str(url))
        #print curlurl
        res = os.popen(curlurl).read()
        print res
        #req = urllib2.Request(url, text, self.HEADERS)
        res = json.loads(res)
        #print res
        #res = urllib2.urlopen(req)
        body = res
        return self.parseResponse(body)

    def buildJson(self, addr1, addr2):
        obj = {}
        obj[ "wifiAccessPoints" ] = self.buildAddressList(addr1, addr2)
        text = json.dumps(obj)
        return text

    def buildJson_array(self, mac_array, p_array):
        obj = {}
        obj[ "wifiAccessPoints" ] = self.buildAddressList2(mac_array, p_array)
        text = json.dumps(obj)
        return text


    def buildAddressList(self, addr1, addr2):
        list = []
        list.append( self.buildAddress(addr1) )
        list.append( self.buildAddress(addr2) )
        return list

    def buildAddressList2(self, mac_array, p_array):
        list = []
        for i,m in enumerate(mac_array):
            if len(m) == 0:
                break
            list.append(self.buildAddress2(m,p_array[i]))
        #list.append( self.buildAddress(addr1) )
        #list.append( self.buildAddress(addr2) )
        return list

    def buildAddress(self, addr):
        dict = { "macAddress": addr}
        return dict

    def buildAddress2(self, addr,power):
        dict = { "macAddress": addr, "signalStrength": power }
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

def generateURL(lat, lng):
    url = "https://maps.google.com/maps?q=" + str(lat) + "," + str(lng) + "&z=12"
    print("This is the URL to visit:")
    print url

def locateself(debug_arg):
    if debug_arg == 1:
        print("Pulling from wifilist")
        os.popen("cat wifilist | grep WPA | sort -r -k3 -n > /tmp/wifi")
        powers = os.popen("cat /tmp/wifi | awk '{print $3}'").read()
        macs = os.popen("cat /tmp/wifi | awk '{print $1}'").read()
        print("Finished getting Wifi\n")
    else:
        print("Scanning for SSIDs")
        os.popen("wpa_cli scan")
        time.sleep(3) # to allow the scan results to populate
        print("Scanning finished!")
        os.popen("wpa_cli scan_results > /tmp/wifi_all")
        print os.popen("cat /tmp/wifi_all").read()
        # Only display WPS enabled points
        os.popen("cat /tmp/wifi_all | grep WPA | sort -r -k3 -n > /tmp/wifi")
        powers = os.popen("cat /tmp/wifi | awk '{print $3}'").read()
        macs = os.popen("cat /tmp/wifi | awk '{print $1}'").read()
    mac_array = macs.split('\n')
    p_array = powers.split('\n')
    geo = GeoWifi()
    res = geo.request_new( KEY, mac_array, p_array )
    if res is None:
        exit()
    #print str(res["lat"]) + " " + str(res["lng"]) + " "+ str(res["accuracy"])
    generateURL( res["lat"], res["lng"] )

if __name__ == "__main__":
    # main
    args = sys.argv
    argc = len(args)
    self_arg = 0
    debug_arg = 0
    for arg in sys.argv:
        if arg == '-self':
            self_arg = 1
        if arg == '-d':
            debug_arg = 1

    if (len(args) < 3 and self_arg == 0):
        print 'Usage: python %s mac_addr_1 mac_addr_2' % args[0]
        exit()
    elif self_arg == 1:
        locateself(debug_arg)
        exit()

    geo = GeoWifi()
    res = geo.request( KEY, args[1], args[2] )
    if res is None:
        exit()

    #print str(res["lat"]) + " " + str(res["lng"]) + " "+ str(res["accuracy"])
    generateURL( res["lat"], res["lng"] )
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
