#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

( cd $DIR/../.. && gradle :newrelic-agent:jar )

( cd $DIR/../../automation/vagrant && ./virtualize-tests.sh $@ )
