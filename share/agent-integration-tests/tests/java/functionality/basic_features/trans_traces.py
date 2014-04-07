#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class TomcatTest(TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7.0}, jvm_args=['-Dnewrelic.config.transaction_tracer.transaction_threshold=1.0'])
    def test_transaction_partialtrace(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/SlowTransactionServlet'))
        
        # verify we hit the servlet
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/SlowTransactionServlet'),
            {'count' : 1})

        tts = self.test_env.collector.get_transaction_traces('WebTransaction/Servlet/SlowTransactionServlet')
        
        for tt in tts:
            tts_with_property = tt.get_segs_with_prop('partialtrace')
            tts_with_backtrace = tt.get_segs_with_prop('backtrace')
            
            # This count does not include the root
            self.assertEqual(len(tts_with_property), 6, "The number of transaction segments with property partialtrace is not equal")
            self.assertEqual(len(tts_with_backtrace), 2, "The number of transaction segments with property backtrace is not equal")
            
            self.assertEqual(tts_with_backtrace[0].metric_name, "Java/javax.servlet.ServletRequestListener/requestInitialized")
            self.assertEqual(tts_with_backtrace[1].metric_name, "Servlet/com.nr.test.servlet.SlowTransactionServlet/service")
            
            self.assertEqual(tts_with_property[0].metric_name, "Custom/com.nr.test.servlet.SlowTransactionServlet/firstMethod")
            self.assertEqual(4, len(tts_with_property[0].params.get('partialtrace')))
            self.assertTrue(tts_with_property[0].params.get('backtrace') is None)
            
            self.assertEqual(tts_with_property[1].metric_name, "Custom/com.nr.test.servlet.SlowTransactionServlet/secondMethod")
            self.assertEqual(1, len(tts_with_property[1].params.get('partialtrace')))
            self.assertEqual('com.nr.test.servlet.SlowTransactionServlet.secondMethod(SlowTransactionServlet.java:33)', tts_with_property[1].params.get('partialtrace')[0])
            self.assertTrue(tts_with_property[1].params.get('backtrace') is None)

            
            self.assertEqual(tts_with_property[2].metric_name, "Custom/com.nr.test.servlet.SlowTransactionServlet/thirdMethod")
            self.assertEqual(1, len(tts_with_property[2].params.get('partialtrace')))
            self.assertTrue(tts_with_property[2].params.get('backtrace') is None)
            self.assertEqual('com.nr.test.servlet.SlowTransactionServlet.thirdMethod(SlowTransactionServlet.java:39)', tts_with_property[2].params.get('partialtrace')[0])

            # this is a child node
            self.assertEqual(tts_with_property[3].metric_name, "Custom/com.nr.test.servlet.SlowTransactionServlet/slowMethodTwo")
            self.assertEqual(1, len(tts_with_property[3].params.get('partialtrace')))
            self.assertTrue(tts_with_property[3].params.get('backtrace') is None)
            self.assertEqual('com.nr.test.servlet.SlowTransactionServlet.slowMethodTwo(SlowTransactionServlet.java:58)', tts_with_property[3].params.get('partialtrace')[0])
            
            self.assertEqual(tts_with_property[4].metric_name, "Custom/com.nr.test.servlet.SlowTransactionServlet/slowMethodOneA")
            self.assertTrue(tts_with_property[4].params.get('backtrace') is None)
            self.assertEqual(1, len(tts_with_property[4].params.get('partialtrace')))
            self.assertEqual('com.nr.test.servlet.SlowTransactionServlet.slowMethodOneA(SlowTransactionServlet.java:46)', tts_with_property[4].params.get('partialtrace')[0])

            # this is a child node
            self.assertEqual(tts_with_property[5].metric_name, "Custom/com.nr.test.servlet.SlowTransactionServlet/slowMethodOneB")
            self.assertEqual(1, len(tts_with_property[5].params.get('partialtrace')))
            self.assertTrue(tts_with_property[5].params.get('backtrace') is None)
            self.assertEqual('com.nr.test.servlet.SlowTransactionServlet.slowMethodOneB(SlowTransactionServlet.java:52)', tts_with_property[5].params.get('partialtrace')[0])
            
            
          
    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7.0}, jvm_args=['-Dnewrelic.config.transaction_tracer.transaction_threshold=1.0', '-Dnewrelic.config.transaction_tracer.max_stack_trace=5'])
    def test_trans_partialtrace_limit(self):    
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/SlowOverLimitTransServlet'))
        
        # verify we hit the servlet
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/SlowOverLimitTransServlet'),
            {'count' : 1})

        tts = self.test_env.collector.get_transaction_traces('WebTransaction/Servlet/SlowOverLimitTransServlet')
        
        for tt in tts:
            tts_with_property = tt.get_segs_with_prop('partialtrace')
            tts_with_backtrace = tt.get_segs_with_prop('backtrace')
            
            # This count does not include the root
            self.assertEqual(len(tts_with_property), 7, "The number of transaction segments with property partialtrace is not equal")
            self.assertEqual(len(tts_with_backtrace), 2, "The number of transaction segments with property backtrace is not equal")
            
            self.assertEqual(tts_with_backtrace[0].metric_name, "Java/javax.servlet.ServletRequestListener/requestInitialized")
            
            self.assertEqual(tts_with_backtrace[1].metric_name, "Servlet/com.nr.test.servlet.SlowOverLimitTransServlet/service")
        
            self.assertEqual(tts_with_property[0].metric_name, "Custom/com.nr.test.servlet.SlowOverLimitTransServlet/run")
            self.assertEqual(tts_with_property[1].metric_name, "Custom/com.nr.test.servlet.SlowOverLimitTransServlet/childInitiator")
            self.assertEqual(tts_with_property[2].metric_name, "Custom/com.nr.test.servlet.SlowOverLimitTransServlet/childfive")
            self.assertEqual(tts_with_property[3].metric_name, "Custom/com.nr.test.servlet.SlowOverLimitTransServlet/childfour")
            self.assertEqual(tts_with_property[4].metric_name, "Custom/com.nr.test.servlet.SlowOverLimitTransServlet/childthree")
            self.assertEqual(tts_with_property[5].metric_name, "Custom/com.nr.test.servlet.SlowOverLimitTransServlet/childtwo")  
            self.assertEqual(tts_with_property[6].metric_name, "Custom/com.nr.test.servlet.SlowOverLimitTransServlet/childone")
            # childsix and childseven should not have stack traces because we have reached the limit of 5 but all parents should


if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
