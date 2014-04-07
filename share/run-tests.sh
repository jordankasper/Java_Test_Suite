#!/bin/bash
#
# run-tests.sh
#
# This script executes within the VM in the local VM case.
# Run the test(s) and exit based on test outcome.

echo 'run-tests.sh: starting ...'

TESTS_TO_RUN='tests/java'
IS_PERFORMANCE=false

# Set the appropriate tests to run
if [ $# -eq 0 ] ; then
  echo "run-tests.sh: No input specified. Running the default test suite: $TESTS_TO_RUN"
else
  TESTS_TO_RUN=$1
  echo "run-tests.sh: Test(s) to run: $TESTS_TO_RUN"
  if [[ $TESTS_TO_RUN == tests/java/performance* ]] ; then
      echo "run-tests.sh: Running the performance tests"
      IS_PERFORMANCE=true
  fi
fi

BASEDIR=/home/jenkins/java_agent/agent-integration-tests

cd ${BASEDIR}

export AIT_STOP_LIST=${BASEDIR}/conf/ait-stop-list.yml

echo "AIT_STOP_LIST file is at $AIT_STOP_LIST"
echo "AIT_STOP_LIST contents:"
/bin/cat $AIT_STOP_LIST

echo 'run-tests.sh: sourcing conf/testenv'
source conf/testenv java

echo 'run-tests.sh: Python version ...'
python -V

export TEST_LOG_LEVEL=INFO #DEBUG
echo "Setting TEST_LOG_LEVEL=$TEST_LOG_LEVEL"

echo "Fetching binary artifacts..."
./bin/reposync.sh

echo "run-tests.sh: running $TESTS_TO_RUN"
./bin/runtest.sh $TESTS_TO_RUN

if $IS_PERFORMANCE ; then
    # Post performance results to a dashboard (see Ashley)
    echo 'run-tests.sh: post results to dashboard'
    /usr/bin/ruby ./bin/post_to_dashboard.rb
fi

# Again perform various cleanups
echo 'run-tests.sh: cleanup'
/bin/ps -eaf | /bin/grep -v grep | /bin/grep tomcat | /bin/grep jenkins | /usr/bin/awk '{print $2}' | /usr/bin/xargs /bin/kill -9 > /dev/null 2>&1
/usr/bin/killall python3

exit $?
