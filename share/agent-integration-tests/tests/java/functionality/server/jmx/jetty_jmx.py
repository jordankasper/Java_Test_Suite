#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class JettyJmxTest(TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : 7.1})
    def test_jmx_older(self):

        self.assertTrue(
            self.test_env.jetty.get_path('/java_test_webapp/TestServlet'))
        
        self.verify_jvm_jmx_common()

        self.assertTrue(
            self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))    


    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [7.3, 7.4, 7.5, 7.6, 8.0, 8.1]})
    def test_jmx_newer(self):

        self.assertTrue(
            self.test_env.jetty.get_path('/java_test_webapp/TestServlet'))
        
        self.verify_jvm_jmx_common()
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/0/Active'))      

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/0/Idle'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/0/Max'))

        self.assertTrue(
            self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))
        
    # this  verifies the common metrics between the different versions of jmx application servers   
    def verify_jvm_jmx_common(self):
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Threads/Thread Count'))      

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Threads/TotalStartedCount')) 

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Classes/Loaded'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Classes/Unloaded'))

      

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
