#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
import time
import newrelic.agenttest.unittest

class CommandsTest(newrelic.agenttest.unittest.TestCase):

    @collector(
        custom={
            'command_options' : [[
                    1,
                    {
                        'name' : 'start_profiler',
                        'arguments' : {
                            'profile_agent_code'    : False,
                            'duration'              : 0.1, 
                            'profile_id'            : 1,
                            'sample_period'         : 0.1,
                            'only_runnable_threads' : False,
                            'only_request_threads'  : False
                        },
                    }
            ]]
        }
    )
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_profile_command(self):
        self.assertTrue(self.test_env.tomcat.get_path('/java_test_webapp/TestServlet'))

        self.assertIterAttributes(
            self.test_env.collector.get_profiles(),
            {
                'profile_id'   : 1,
                'start_time'   : time.time() - 60,
                'end_time'     : time.time() - 60,
                'thread_count' : 0,
                'sample_count' : 0,
            },
            start_time=self.assertGreater,
            end_time=self.assertGreater,
            thread_count=self.assertGreater,
            sample_count=self.assertGreater)

        self.assertGreater(self.test_env.collector.get_profiles()[0].size(), 0)

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
