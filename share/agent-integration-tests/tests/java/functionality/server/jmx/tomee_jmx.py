#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class TomEEJmxTest(TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomee
    def test_jmx(self):

        self.assertTrue(
            self.test_env.tomee.get_path('/java_test_webapp/TestServlet'))
        
        self.verify_jvm_jmx_common()
        
        # session information  
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/tomee/Active'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/tomee/Expired'))
                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/tomee/Rejected'))
                        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/tomee/AverageAliveTime'))
                                
    
        # active
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"ajp-bio-8009"/Active'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"http-bio-8080"/Active'))
        
        # idle
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"ajp-bio-8009"/Idle'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"http-bio-8080"/Idle'))
        
        # max
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"ajp-bio-8009"/Max'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"http-bio-8080"/Max'))
        
        
        self.assertTrue(
            self.test_env.tomee.get_path_and_shutdown('/java_test_webapp/TestServlet'))

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
