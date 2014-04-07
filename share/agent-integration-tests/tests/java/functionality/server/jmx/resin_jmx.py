#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class ResinJmxTest(TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @resin(select={'version' : 3.1})
    def test_jmx_31(self):

        self.assertTrue(
            self.test_env.resin.get_path('/java_test_webapp/TestServlet'))
        
        self.verify_jvm_jmx_common()
        self.verify_resin_jmx_common()

        # shutdown application server
        self.assertTrue(
            self.test_env.resin.get_path_and_shutdown('/java_test_webapp/TestServlet'))
        

        
        
    @collector
    @java_agent
    @java
    @java_test_webapp
    @resin(select={'version' : 4})
    def test_jmx_4(self):

        self.assertTrue(
            self.test_env.resin.get_path('/java_test_webapp/TestServlet'))
        
        self.verify_jvm_jmx_common()
        self.verify_resin_jmx_common()
        
        # shutdown application server
        self.assertTrue(
            self.test_env.resin.get_path_and_shutdown('/java_test_webapp/TestServlet'))
        
        # transaction information
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Transactions/Currently/Active'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Transactions/Outcome/Committed'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Transactions/Outcome/Rolled Back'))
        
        
          
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
        
    def verify_resin_jmx_common(self):
        
        # Thread count information
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/Resin/Active'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/Resin/Idle'))

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/Resin/Max'))
        
        # session information
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Active'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Expired'))
        
            

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
