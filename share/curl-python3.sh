#!/bin/sh

TEMPDIR=`/bin/mktemp -d`

cd $TEMPDIR
#/usr/bin/curl -O http://python-distribute.org/distribute_setup.py
/bin/cp /deploy_scripts/distribute_setup.py .
/usr/bin/python3 ./distribute_setup.py
/bin/tar -xf /deploy_scripts/PyYAML-3.10.tar.gz

cd PyYAML-3.10
/usr/bin/python3 setup.py install

cd $TEMPDIR
#/usr/bin/curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
/bin/cp /deploy_scripts/get-pip.py .
/usr/bin/python3 ./get-pip.py
/usr/local/bin/pip install virtualenv

rm -rf $TEMPDIR

exit 0
