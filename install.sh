#!/bin/bash

cd $(dirname $0)

if [ ! -d RokuSDK ] ; then
	wget http://wwwimg.roku.com/static/sdk/RokuSDK.zip
	unzip RokuSDK
fi

if [ ! -d env ] ; then
	virtualenv --no-site-packages env
fi
source env/bin/activate
pip install -r requirements.txt

if [ ! -f credentials.ini ] ; then
	expect <<-EOF >expect.output
	spawn telnet $(python control.py --which | cut -d: -f2 | tr -d '/') 8080
	expect ">"
	send "genkey\n"
	expect ">"
	send "quit\n"
	EOF

	echo "[Roku Developer]" > credentials.ini
	cat expect.output | grep '^\(Password\|DevID\): \(.\+\)$' | tr ':' '=' >> credentials.ini
	#rm expect.output
fi
