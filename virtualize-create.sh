#!/bin/sh
#
# virtualize-create.sh - implementation of gradle vagrantCreateVM task
#
# This script is called from gradle to create a VM on the local host to run the AITs.
# We are running in the automation/vagrant directory so can issue Vagrant commands
#

echo 'virtualize-create.sh: starting...'
TEMPSSHFILE=/tmp/cfg$$

# 1 - Bring up the VM
echo 'virtualize-create.sh: bringing up the VM ...'
vagrant up
vagrant ssh-config > $TEMPSSHFILE

# 2 - Copy Files to Correct Locations in Share
# The share directory is a shared file system which gets mapped to deploy_scripts in the vm.
# We want to place the AIT tests and the newrelic.jar to test in the share directory
# so that we have access to them in the vm.

echo 'virtualize-create.sh: delete old agent from vagrant share...'
rm -rf share/agent_under_test/

echo 'virtualize-create.sh: copy new agent to vagrant share'
mkdir share/agent_under_test
cp ../../newrelic-agent/build/libs/newrelic.jar share/agent_under_test/newrelic.jar

echo 'virtualize-create.sh: deleting integration tests from vagrant share...'
rm -rf share/agent-integration-tests/

echo 'virtualize-create.sh: copying tests from work view to vagrant share...'
mkdir share/agent-integration-tests
mkdir share/agent-integration-tests/bin
cp -pR ../../agent-integration-tests/bin/*.sh  share/agent-integration-tests/bin
cp -pR ../../agent-integration-tests/bin/*.rb  share/agent-integration-tests/bin
cp -pR ../../agent-integration-tests/conf  share/agent-integration-tests/conf
cp -pR ../../agent-integration-tests/src  share/agent-integration-tests/src
cp -pR ../../agent-integration-tests/testapps  share/agent-integration-tests/testapps
cp -pR ../../agent-integration-tests/tests  share/agent-integration-tests/tests

# 3 - Run the reposync script in the vm 
echo 'virtualize-create.sh: executing run-setup.sh in the VM ...'
ssh jenkins@default -F $TEMPSSHFILE "/bin/bash /deploy_scripts/run-setup.sh"
echo 'virtualize-create.sh: ... back, cleaning up the VM ...'

echo 'virtualize-create.sh: exit code ' $EXITSTATUS
exit $EXITSTATUS
