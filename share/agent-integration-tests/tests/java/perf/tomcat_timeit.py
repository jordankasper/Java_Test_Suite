#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer
from newrelic.agenttest.app.java.metrics.testmetrics import *
import timeit
import math


class TomcatTimeitTest(TestCase):
    
    all_metrics = None
    servlet_name = None
    headers = None
    the_data = None
    successes = None
    
    @classmethod
    def setUpClass(cls):
        super(TomcatTimeitTest, cls).setUpClass()
        global  all_metrics
        all_metrics = TestMetrics("sec")
        
    @classmethod
    def tearDownClass(cls):
        global all_metrics
        all_metrics.report_metric()
        super(TomcatTimeitTest, cls).tearDownClass()
        
        
    def call_servlet(self):
        global servlet_name, headers, the_data, successes
        self.test_env.tomcat.get_path('/java_test_webapp/' + servlet_name, data=the_data, headers=headers)
        successes.append(self.test_env.tomcat.get_response_header('was_success'))
        
    def perform_work(self, framework, test_name):
        # get all of the variables
        global servlet_name, headers, the_data, successes
        servlet_name = self.test_env.metric_servlet.get_name()
        iter_count = self.test_env.metric_servlet.get_iter_count()
        repeat_count = self.test_env.metric_servlet.get_repeat_count()
        report_type = self.test_env.metric_servlet.get_report_type()
        summary = self.test_env.metric_servlet.is_summary()
        
        headers = { 'iteration_count' : 1 }
        the_data = None
        successes = []
        
        # warm it up once
        self.call_servlet();
        #do the timing
        time = (timeit.Timer(self.call_servlet).repeat(repeat=int(repeat_count), number=iter_count))
        
        # shutdown
        self.test_env.tomcat.get_path_and_shutdown('/java_test_webapp/' + servlet_name, data=the_data, headers=headers)

        global all_metrics
        for bool in successes:
            self.assertTrue(bool)

        all_metrics.add_metric(servlet_name, report_type, test_name, framework, min(time), iter_count, self.test_env.tomcat.config_name, self.test_env.tomcat.version, summary)

    
# Run without the agent (agent enabled is false)
    @collector
    @java_agent
    @java(select={'version' : 7})
    @java_test_webapp
    @tomcat(select={'version' : 7}, jvm_args=['-Dnewrelic.config.enabled=false'])
    @metric_servlet
    def test_disabled(self):
        
        self.perform_work('TomcatTimeitTest', 'disabled')
        
#Run with agent but custom methods are not traced
    @collector
    @java_agent
    @java(select={'version' : 7})
    @java_test_webapp
    @tomcat(select={'version' : 7}, jvm_args=['-Dnewrelic.config.log_level=info', '-Dnewrelic.config.agent_enabled=true', '-Dnewrelic.config.audit_mode=false'])
    @metric_servlet
    def test_enabled(self):
        
        self.perform_work('TomcatTimeitTest', 'enabled')

#Run with custom methods in metric_ext.xml traced with log level set to info like customer
    @collector
    @java_agent(custom={'use_metric_ext' : False})
    @java(select={'version' : 7})
    @java_test_webapp
    @tomcat(select={'version' : 7}, jvm_args=['-Dnewrelic.config.log_level=finest', '-Dnewrelic.config.agent_enabled=true', '-Dnewrelic.config.audit_mode=true'])
    @metric_servlet
    def test_enabled_logging(self):
        
        self.perform_work('TomcatTimeitTest', 'enabled_logging')


if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
