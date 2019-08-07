#!/bin/sh

. defaults.sh

for i in jm_cli jm_lib; do
	rm -rf $PYTHON_SITE/$i
done

rm -f /usr/local/bin/jm
rm -f /usr/local/etc/rc.d/jm
