#!/bin/bash

if [ ! -d $(dirname $0)/RokuSDK ] ; then
	wget http://wwwimg.roku.com/static/sdk/RokuSDK.zip
	unzip RokuSDK
fi
