#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class GlassfishTest(TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish
    def test_jmx(self):

        self.assertTrue(
            self.test_env.glassfish.get_path('/java_test_webapp/SlowTransactionServlet'))
        
        self.verify_jvm_jmx_common()
        
        self.assertTrue(
            self.test_env.glassfish.get_path_and_shutdown('/java_test_webapp/TestServlet'))
        

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
