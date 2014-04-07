#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class TomcatJmxTest(TestCase):
    
    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 5.5})
    def test_jmx_55(self):
        self.assertTrue(self.test_env.tomcat.get_path('/java_test_webapp/CustomTestServlet'))
        
        # no jvm metrics for 5.5

        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Active', timeout=90))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Expired'))
                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Rejected'))
                        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/AverageAliveTime'))
                                
        # active
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/http-8080/Active'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/jk-8009/Active'))
        
        # idle
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/http-8080/Idle'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/jk-8009/Idle'))
        
        # max
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/http-8080/Max'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/jk-8009/Max'))
        
        # shutdown the server
        self.test_env.tomcat.shutdown()
          
    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 6})
    def test_jmx_6(self):
        self.assertTrue(self.test_env.tomcat.get_path('/java_test_webapp/CustomTestServlet'))

        self.verify_jvm_jmx_common()
        
        self.assertTrue(self.test_env.tomcat.get_path('/java_test_webapp/CustomTestServlet'))

        # session information  
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Active', timeout=90))
                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Expired'))
                        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Rejected'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/AverageAliveTime'))  
    
        # active
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/http-8080/Active'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/jk-8009/Active'))
        
        # idle
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/http-8080/Idle'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/jk-8009/Idle'))
        
        # max
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/http-8080/Max'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/jk-8009/Max'))

        # shutdown the server
        self.test_env.tomcat.shutdown()

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_jmx_7(self):
        self.assertTrue(self.test_env.tomcat.get_path('/java_test_webapp/CustomTestServlet'))

        self.verify_jvm_jmx_common()
        
        self.assertTrue(self.test_env.tomcat.get_path('/java_test_webapp/CustomTestServlet'))
        
        # active
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Active', timeout=90))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/host-manager/Active'))
                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/docs/Active'))
                        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/manager/Active'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/examples/Active'))
        
        # rejected
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Rejected'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/host-manager/Rejected'))
                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/docs/Rejected'))
                        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/manager/Rejected'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/examples/Rejected'))
        
         # expired
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/Expired'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/host-manager/Expired'))
                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/docs/Expired'))
                        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/manager/Expired'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/examples/Expired'))
        
        # avg alive time
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/java_test_webapp/AverageAliveTime'))
        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/host-manager/AverageAliveTime'))
                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/docs/AverageAliveTime'))
                        
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/manager/AverageAliveTime'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/Session/examples/AverageAliveTime'))
        
        # active
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"http-bio-8080"/Active'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"ajp-bio-8009"/Active'))
        
        # idle
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"http-bio-8080"/Idle'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"ajp-bio-8009"/Idle'))
        
        # max
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"http-bio-8080"/Max'))
                                
        self.assertNotNull(
            self.test_env.collector.get_unscoped_metrics('JmxBuiltIn/ThreadPool/"ajp-bio-8009"/Max'))
        
        # shutdown the server
        self.test_env.tomcat.shutdown()

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
