#!/bin/sh

. defaults.sh

INSTALL="/usr/bin/install -o root -g wheel"

for i in jm_cli jm_lib; do
	mkdir -p $PYTHON_SITE/$i
	for file in $i/*.py; do
		echo $file -\> $PYTHON_SITE/$i
		$INSTALL $file $PYTHON_SITE/$i
	done
done

echo jm -\> /usr/local/bin
$INSTALL -m 0755 jm /usr/local/bin

echo rc.d/jm -\> /usr/local/etc/rc.d
$INSTALL -m 0755 rc.d/jm /usr/local/etc/rc.d

