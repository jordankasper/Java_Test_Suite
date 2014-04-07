#!/bin/sh
#
# virtualize-tests.sh - implementation of gradle vagrantFunctAIT and vagrantPerfAIT tasks
#
# This script is called from gradle to run the AITs in a VM on the local host.
# It is also called by jenkins to run the AITS on a slave node.
# We are running in the automation/vagrant directory so can issue Vagrant commands
#

echo 'virtualize-tests.sh: starting...'
TEMPSSHFILE=/tmp/cfg$$
RESULTSFILE=/tmp/results$$.txt
# Note: tests/java includes all of the tests. tests/java/performance are the performance tests 
# and tests/java/functionality are the tests which verify basic functionality
TESTS_TO_RUN=tests/java/

if [ $# -eq 0 ] ; then
  echo "virtualize-tests.sh: No input specified. Running the default test suite: $TESTS_TO_RUN"
else
  TESTS_TO_RUN=$1
  echo "virtualize-tests.sh: Test(s) to run: $TESTS_TO_RUN"
fi

# 1 - Bring up the VM
echo 'virtualize-tests.sh: bringing up the VM ...'
vagrant up
vagrant ssh-config > $TEMPSSHFILE


# 2 - Copy Files to Correct Locations in Share
# The share directory is a shared file system which gets mapped to deploy_scripts in the vm.
# We want to place the AIT tests and the newrelic.jar to test in the share directory
# so that we have access to them in the vm.

echo 'virtualize-test.sh: delete old agent from vagrant share...'
rm -rf share/agent_under_test/

echo 'virtualize-test.sh: copy new agent to vagrant share'
mkdir share/agent_under_test
cp ../../newrelic-agent/build/libs/newrelic.jar share/agent_under_test/newrelic.jar

echo 'virtualize-tests.sh: deleting integration tests from vagrant share...'
rm -rf share/agent-integration-tests/

echo 'virtualize-tests.sh: copying tests from work view to vagrant share...'
mkdir share/agent-integration-tests
mkdir share/agent-integration-tests/bin
cp -pR ../../agent-integration-tests/bin/*.sh  share/agent-integration-tests/bin
cp -pR ../../agent-integration-tests/bin/*.rb  share/agent-integration-tests/bin
cp -pR ../../agent-integration-tests/conf  share/agent-integration-tests/conf
cp -pR ../../agent-integration-tests/src  share/agent-integration-tests/src
cp -pR ../../agent-integration-tests/testapps  share/agent-integration-tests/testapps
cp -pR ../../agent-integration-tests/tests  share/agent-integration-tests/tests

# 3 - Run the test script in the vm 
# run-tests.sh should perform final setup in the vm and then run the tests
# this file can be found in the share directory on this box or under deploy_scripts in the vm
echo 'virtualize-tests.sh: executing test driver (run-tests.sh) in the VM ...'
ssh jenkins@default -F $TEMPSSHFILE "/bin/bash /deploy_scripts/run-tests.sh $TESTS_TO_RUN 2>&1|tee  $RESULTSFILE"
echo 'virtualize-tests.sh: ... back, cleaning up the VM ...'


# 4 - Clean up and show results
scp -F $TEMPSSHFILE jenkins@default:$RESULTSFILE $RESULTSFILE
/bin/rm -f $TEMPSSHFILE
vagrant halt

echo 'virtualize-tests.sh: RESULTSFILE follows ...'
cat $RESULTSFILE

EXITSTATUS=0
if grep '^FAILED (' $RESULTSFILE > /dev/null
 then
  EXITSTATUS=1
 fi
/bin/rm -f $RESULTSFILE

echo 'virtualize-tests.sh: exit code ' $EXITSTATUS
exit $EXITSTATUS
