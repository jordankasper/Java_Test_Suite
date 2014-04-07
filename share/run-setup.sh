#!/bin/bash
#
# run-setup.sh
#
# This script executes within the VM in the local VM case.
# Copy files to the correct location, source the test environment, reposync.

echo 'run-setup.sh: starting ...'

# If there is an agent-integration-tests directory in the vagrant share area (/deploy_scripts),
# update the tests (in ~jenkins) from the share content. This has the effect of injecting the
# developer's latest work into the local VM. The implementation is a bit tricky because we don't
# want to copy the entire agent-integration-tests directory - the bin/ and conf/ directories
# have been carefully configured by other shell scripts. Also, we
# move the previous tests out of the way for possible examination / diffing.
if [ -d /deploy_scripts/agent-integration-tests ] ; then
	echo 'run-setup.sh: AITs found in /deploy_scripts ...'
	if [ -d /home/jenkins/java_agent/agent-integration-tests.prev ] ; then
		echo 'run-setup.sh: discarding second previous test directory ...'
		rm -rf /home/jenkins/java_agent/agent-integration-tests.prev
	fi
	if [ -d /home/jenkins/java_agent/agent-integration-tests ] ; then
		echo 'run-setup.sh: moving previous tests to tests.prev ...'
		mkdir /home/jenkins/java_agent/agent-integration-tests.prev
		mv /home/jenkins/java_agent/agent-integration-tests/* /home/jenkins/java_agent/agent-integration-tests.prev/
	fi
        if [ ! -d /home/jenkins/java_agent/agent-integration-tests ] ; then
                echo 'run-setup.sh: making agent-integration-tests ...'
                mkdir /home/jenkins/java_agent/agent-integration-tests
        fi

	echo 'run-setup.sh: copying in new tests from /deploy_scripts to /home/jenkins/java_agent/agent-integration-tests...'
	cp -pR /deploy_scripts/agent-integration-tests/* /home/jenkins/java_agent/agent-integration-tests/
fi

# Verify that the agent-integration-tests are present
if [ ! -d /home/jenkins/java_agent/agent-integration-tests ] ; then
        # The string 'FAILED (' must appear in column 1 for our caller to detect the failure.
        echo 'FAILED (config): run-setup.sh: unable to find /home/jenkins/java_agent/agent-integration-tests .... exiting'
        exit 1
fi

# Copy correct configuration files - the correct java_local_config must be put into place
if [ ! -d /deploy_scripts/java_local_config.yml ] ; then
        echo 'run-setup.sh: Adding correct configuration files...'
        cp /deploy_scripts/java_local_config.yml /home/jenkins/java_agent/agent-integration-tests/conf/java_local_config.yml
else
        # The string 'FAILED (' must appear in column 1 for our caller to detect the failure.
        echo 'FAILED (config): run-setup.sh: unable to find /deploy_scripts/java_local_config.yml ... exiting without running tests'
        exit 1
fi

echo 'run-setup.sh: make bin scripts executable'
chmod 700 /home/jenkins/java_agent/agent-integration-tests/bin/*

if [ -x /home/jenkins/apache-maven-3.1.0/bin/mvn ] ; then
         echo 'run-setup.sh: Adding link to maven in bin ...'
         ln -s /home/jenkins/apache-maven-3.1.0/bin/mvn /home/jenkins/java_agent/agent-integration-tests/bin/
else
        # The string 'FAILED (' must appear in column 1 for our caller to detect the failure.
        echo 'FAILED (mvn): run-setup.sh: unable to find /home/jenkins/apache-maven-3.1.0/bin/mvn ... exiting without running tests'
        exit 1
fi

if [ -f /home/jenkins/java_agent/agent-integration-tests/conf/testenv ] ; then
        echo 'run-setup.sh: Set testenv perms to be correct...'
        chmod 700 /home/jenkins/java_agent/agent-integration-tests/conf/testenv
else
        # The string 'FAILED (' must appear in column 1 for our caller to detect the failure.
        echo 'FAILED (testenv): run-setup.sh: unable to find testenv ... exiting'
        exit 1
fi

BASEDIR=/home/jenkins/java_agent/agent-integration-tests

# This may need to move somewhere else. It sets the path to the test "stop list", a .yml
# defining tests to be skipped on this test run. The .yml is processed in TestEnv.__init__()
# and checked on each call to unittest.main().

export AIT_STOP_LIST=${BASEDIR}/conf/ait-stop-list.yml

cd ${BASEDIR}

/usr/local/bin/virtualenv .
./bin/pip install -r conf/requirements.txt

echo 'run-test.sh: sourcing conf/testenv'
source conf/testenv java

echo 'run-setup.sh: performing reposync ...'
if ./bin/reposync.sh ; then
	echo 'run-setup.sh: reposync complete'
else
        # The string 'FAILED (' must appear in column 1 for our caller to detect the failure.
	echo 'FAILED (reposync): run-setup.sh: reposync FAILED'
	exit 1
fi

echo 'run-setup.sh: Python version ...'
python -V

export TEST_LOG_LEVEL=INFO
#export TEST_LOG_LEVEL=DEBUG
echo "run-setup.sh: Setting TEST_LOG_LEVEL=$TEST_LOG_LEVEL"

exit $?
