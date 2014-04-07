#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class JBossJmxTest(TestCase):
    
    @collector
    @java_agent
    @java
    @java_test_webapp
    @jboss(select={'version' : 6.1})
    def test_jmx_6(self):

        self.assertTrue(
            self.test_env.jboss.get_path('/java_test_webapp/TestServlet'))
        
        self.verify_jvm_jmx_common()
        
        self.assertTrue(
            self.test_env.jboss.get_path('/java_test_webapp/TestServlet'))
        
        # Thread pool information
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/http-127.0.0.1-8080/Active', timeout=90))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/http-127.0.0.1-8080/Idle'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/ajp-127.0.0.1-8009/Max'))
        
        # session information
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Active'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Rejected'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Expired'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/AverageAliveTime'))

        # shutdown the server
        self.test_env.jboss.shutdown()

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jboss(select={'version' : 7.1})
    def test_jmx_7(self):

        self.assertTrue(
            self.test_env.jboss.get_path('/java_test_webapp/TestServlet'))
        
        self.verify_jvm_jmx_common()
        
        self.assertTrue(
            self.test_env.jboss.get_path('/java_test_webapp/TestServlet'))
        
        # transaction information
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Transactions/Currently/Active', timeout=90))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Transactions/Outcome/Committed'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Transactions/Outcome/Rolled Back'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Transactions/Created/Nested'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Transactions/Created/Top Level'))

        # shutdown the server
        self.test_env.jboss.shutdown()

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
