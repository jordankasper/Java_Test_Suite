#!/bin/bash
#
# runtest.sh - run a group of tests or a single test.
#
# Arguments are processed in order. If a directory, all .py files under the directory are
# added to the test list. If a plain file, the file is added to the test list. If neither,
# the argument is added to the list of arguments passed to each test.
#
# Jan 2014 when a single directory argument is passed, the list of .py files under the
# directory is now sorted. When all the tests are run in the "usual way" (by passing the
# tests/java directory on the command line), the tests will always be run in the same
# order. Multiple individual tests will be run in the order specified, however. If 
# multiple directories are given on the command line, the tests within each directory
# hierarchy will be sorted but the entire list will not; this case is obscure.

declare -a TESTS

echo "runtest.sh: firing up..."
echo "runtest.sh: all tests to run $@"

IN_DIR_OR_TEST=$@

for t in "$@"; do
	if [[ -d "$t" ]]; then
                # Generate the test list and emit some basic statistics
                export TEST_LIST=$(find $IN_DIR_OR_TEST -name '*.py' | sort)
                NUM_TEST_FILES=$( /bin/echo $TEST_LIST | wc -w)
                NUM_TESTS=$(grep '@java_agent' $TEST_LIST | wc -l)
                NUM_COMMENTED_OUT=$(grep '^#.*@java_agent' $TEST_LIST | wc -l)
                echo "runtest.sh: $NUM_TEST_FILES AIT source files"
                echo "runtest.sh: $NUM_TESTS AIT methods found"
                echo "runtest.sh: stop list follows ..."
                cat ${AIT_STOP_LIST} /dev/null
                echo "runtest.sh: end of stop list."

                # Add to test list
		for f in ${TEST_LIST}; do
			TESTS[${#TESTS[@]}]="$f"
		done
	elif [[ -f "$t" ]]; then
		TESTS[${#TESTS[@]}]="$t"
	else
		TEST_ARGS[${#TEST_ARGS[@]}]="$t"
	fi
done

GLOBAL_STATUS=0
for t in "${TESTS[@]}"; do
	# note that this cleanup kills processes belonging to the jenkins user.  It will have no effect when tests are running as a non-jenkins user
	
	echo "runtest.sh: running test $t..."
	"$t" "-v" "${TEST_ARGS[@]}"
	STATUS=$?
	if [[ $STATUS -ne 0 ]]; then
		echo "test $t failed"
		GLOBAL_STATUS=$STATUS
		#short circuit the test run to abort on the first failure.  
		#Comment the following line to run all tests even after one failure, uncomment to fail fast.
		#echo "runtest.sh: test run failed - fail fast enabled"
		#exit $STATUS
	fi
done

if [[ $GLOBAL_STATUS -ne 0 ]]; then
	echo "runtest.sh: test run failed"
	exit $GLOBAL_STATUS
fi

echo "runtest.sh: test run OK"
exit $GLOBAL_STATUS
