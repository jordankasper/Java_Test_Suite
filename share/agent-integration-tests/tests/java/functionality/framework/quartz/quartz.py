#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer
from http.client import HTTPResponse

class QuartzTest(TestCase):

    @collector
    @java_agent
    @java
    @quartz_test(custom={'quartz.version': '2.2.1'})
    @tomcat(select={'version' : 7})
    def test_quartz_2_2_1(self):
        self._test_quartz()

    @collector
    @java_agent
    @java
    @quartz_test(custom={'quartz.version': '2.1.6'})
    @tomcat(select={'version' : 7})
    def test_quartz_2_1_6(self):
        self._test_quartz()
 
    @collector
    @java_agent
    @java
    @quartz_test(custom={'quartz.version': '2.0.2'})
    @tomcat(select={'version' : 7})
    def test_quartz_2_0_2(self):
        self._test_quartz()
 
    @collector
    @java_agent
    @java
    @quartz_test(custom={'quartz.version': '1.8.6'})
    @tomcat(select={'version' : 7})
    def test_quartz_1_8_6(self):
        self._test_quartz()

    @collector
    @java_agent
    @java
    @quartz_test(custom={'quartz.version': '1.7.3'})
    @tomcat(select={'version' : 7})
    def test_quartz_1_7_3(self):
        self._test_quartz()
        
    def _test_quartz(self):
        result = self.test_env.tomcat.get_path_and_shutdown('/quartz-test/')
        self.assertTrue(result)

#        metrics = self.test_env.collector.get_unscoped_metrics()
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('Java/com.nr.test.quartz.TestJob/execute'),
                                  { 'count' : 1 })
         
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('OtherTransaction/Job/com.nr.test.quartz.TestJob/execute'),
                                  { 'count' : 1 })

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
