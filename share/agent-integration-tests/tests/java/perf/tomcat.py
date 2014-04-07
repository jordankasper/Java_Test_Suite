#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer
from newrelic.agenttest.app.java.metrics.testmetrics import *


class TomcatMetricTest(TestCase):
    
    all_metrics = None
    
    @classmethod
    def setUpClass(cls):
        super(TomcatMetricTest, cls).setUpClass()
        global  all_metrics
        all_metrics = TestMetrics("ms")
        
    @classmethod
    def tearDownClass(cls):
        global all_metrics
        all_metrics.report_metric()
        all_metrics.write_metric_summary()
        super(TomcatMetricTest, cls).tearDownClass()
        
    def run_test(self, framework, test_name, is_metrics):
        # get the properties
        servlet_name = self.test_env.metric_servlet.get_name()
        iter_count = self.test_env.metric_servlet.get_method_count()
        repeat_count = self.test_env.metric_servlet.get_repeat_count()
        report_type = self.test_env.metric_servlet.get_report_type()
        summary = self.test_env.metric_servlet.is_summary()

        # run the test
        headers = { 'iteration_count' : iter_count, 'repeat_count' : repeat_count }
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/java_test_webapp/' + servlet_name, data=None, headers=headers, timeout=90))

        # check some properties to verify the test ran as desired
        if(is_metrics):
            self.assertIterAttributes(
                self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/' + servlet_name),
                  {'count': 1})

        self.assertStringEqual(str(iter_count), self.test_env.tomcat.get_response_header('iteration_count'))
        self.assertStringEqual(str(repeat_count), self.test_env.tomcat.get_response_header('repeat_count'))
        self.assertStringEqual("True", self.test_env.tomcat.get_response_header('was_success'))

        global all_metrics
        all_metrics.add_metric(servlet_name, report_type, test_name, framework, self.test_env.tomcat.get_response_header('result_time_sec'), iter_count, self.test_env.tomcat.config_name, self.test_env.tomcat.version, summary)
        
    # Run without the agent (agent enabled is false)
    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7}, jvm_args=['-Dnewrelic.config.enabled=false'])
    @metric_servlet
    def test_agent_disabled(self):
        
        self.run_test('TomcatMetricTest', 'disabled', False)

    # Run with custom methods in metric_ext.xml traced with log level set to info like customer
    @collector
    @java_agent(custom={'use_metric_ext' : True})
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7}, jvm_args=['-Dnewrelic.config.log_level=info', '-Dnewrelic.config.audit_mode=false'])
    @metric_servlet
    def test_agent_trace(self):
        
        self.run_test('TomcatMetricTest', 'enabled', True)


    # Run with custom methods in metric_ext.xml traced with full logging
    @collector
    @java_agent(custom={'use_metric_ext' : True})
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7}, jvm_args=['-Dnewrelic.config.log_level=finest', '-Dnewrelic.config.audit_mode=true'])
    @metric_servlet
    def test_agent_trace_logging(self):

        self.run_test("TomcatMetricTest", "enabled_logging", True)

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
