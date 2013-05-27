#!/bin/bash

# Identify a Roku on the network
# You will need to have enabled the developer interface on your Roku:
# Home 3x, Up 2x, Right, Left, Right, Left, Right

# Determine all IP addresses on all network interfaces
for IP_ADDRESS in $(ifconfig | grep -oE "inet [0-9\.]+" | cut -d\  -f2) ; do
	if [ "${IP_ADDRESS}" != "127.0.0.1" ] ; then
		# Scan for open telnet ports on local subnet
		nmap --open -p22 -oG - ${IP_ADDRESS}/24 | grep ''
	fi
done
