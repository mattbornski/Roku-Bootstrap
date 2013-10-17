#!/usr/bin/env python

import argparse
import requests
import socket
import sys
import time
import xml.dom.minidom
import xpath

SSDP_IP = '239.255.255.250'
SSDP_PORT = 1900
SSDP_WAIT_SECONDS = 1

HULU_PLUS_APP_ID = '2285'
PANDORA_APP_ID = '28'
QUIRKY_APP_ID = '27792_7a2e'
TUNEIN_APP_ID = '1453'

def discover():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	try:
		s.seckopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	except AttributeError:
		pass
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
	s.setblocking(0)

	s.sendto('''M-SEARCH * HTTP/1.1
Host: {SSDP_IP}:{SSDP_PORT}
Man: "ssdp:discover"
MX: {SSDP_WAIT_SECONDS}
ST: roku:ecp
'''.format(SSDP_IP=SSDP_IP, SSDP_PORT=SSDP_PORT, SSDP_WAIT_SECONDS=SSDP_WAIT_SECONDS), (SSDP_IP, SSDP_PORT))
	tSent = time.time()

	# Receiver is supposed to wait a certain period and then broadcast response
	locations = set()
	while time.time() - tSent < SSDP_WAIT_SECONDS + 1:
		try:
			(data, addr) = s.recvfrom(1024)
		except socket.error:
			time.sleep(0.1)
			continue
		rokuDevice = False
		location = None
		for line in data.splitlines():
			if line == 'ST: roku:ecp':
				rokuDevice = True
			if line.startswith('Location: '):
				location = line.split('Location: ', 1)[1]
		if rokuDevice is True and location is not None:
			locations.add(location.split(':')[1].replace('/', ''))
	s.close()
	return locations

def command(rokuLocation, method, path):
	url = 'http://' + rokuLocation + ':8060/' + path.lstrip('/')
	print ' '.join([method, url])
	response = requests.request(method, url)
	assert response.status_code == 200, response.text
	return response

def hasApp(rokuLocation, appId):
	response = command(rokuLocation, 'GET', '/query/apps')
	responseDocument = xml.dom.minidom.parseString(response.text)
	return (xpath.find('//app[@id="{appId}"]'.format(appId=appId), responseDocument) + [None])[0] is not None

def tunein(rokuLocation):
	if hasApp(rokuLocation, TUNEIN_APP_ID):
		for key in ['/launch/{TUNEIN_APP_ID}'.format(TUNEIN_APP_ID=TUNEIN_APP_ID), '/keypress/down', '/keypress/select', '/keypress/select']:
			command(rokuLocation, 'POST', key)
			time.sleep(1.0)

def rockout(rokuLocation):
	if hasApp(rokuLocation, PANDORA_APP_ID):
		for key in ['/launch/{PANDORA_APP_ID}'.format(PANDORA_APP_ID=PANDORA_APP_ID), '/keypress/down', '/keypress/select']:
			while True:
				response = command(rokuLocation, 'POST', key)
				if response.status_code == 200:
					break
				time.sleep(1.0)

def dailyshow(rokuLocation):
	if hasApp(rokuLocation, HULU_PLUS_APP_ID):
		for key in ['/launch/{HULU_PLUS_APP_ID}?search=The+Daily+Show'.format(HULU_PLUS_APP_ID=HULU_PLUS_APP_ID)]:
			while True:
				response = command(rokuLocation, 'POST', key)
				if response.status_code == 200:
					break
				time.sleep(1.0)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Control your Roku')
	# Actions
	actions = parser.add_mutually_exclusive_group(required=True)
	actions.add_argument('--tunein', action='store_true', default=False, help='Launch TuneIn')
	actions.add_argument('--rockout', action='store_true', default=False, help='Launch Pandora')
	actions.add_argument('--dailyshow', action='store_true', default=False, help='Play The Daily Show')
	# Targets
	parser.add_argument('--discover', action='store_true', default=False, help='Discover IP addresses of Rokus on local network')
	args = parser.parse_args(sys.argv[1:])

	rokuLocations = discover()
	if not args.discover:
		# TODO read from command line
		rokuLocations = []

	for rokuLocation in rokuLocations:
		if args.tunein:
			tunein(rokuLocation)
		elif args.rockout:
			rockout(rokuLocation)
		elif args.dailyshow:
			dailyshow(rokuLocation)
		elif args.discover:
			print rokuLocation