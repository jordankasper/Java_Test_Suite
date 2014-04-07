#!/bin/bash

echo 'reposync.sh: start'

if python3 ./src/newrelic/agenttest/reposync.py ; then
	echo 'reposync.sh: success'
	exit 0
else
	echo 'reposync.sh: FAILED'
	exit 1
fi
