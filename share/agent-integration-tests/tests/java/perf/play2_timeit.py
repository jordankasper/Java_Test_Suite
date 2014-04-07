#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer
from newrelic.agenttest.app.java.metrics.testmetrics import *
import timeit
import time
import math
import subprocess


class Play2TimeitTest(TestCase):
    
    all_metrics = None
    servlet_name = None
    headers = None
    the_data = None
    successes = None
    
    @classmethod
    def setUpClass(cls):
        super(Play2TimeitTest, cls).setUpClass()
        global  all_metrics
        all_metrics = TestMetrics("sec")
        
    @classmethod
    def tearDownClass(cls):
        global all_metrics
        all_metrics.report_metric()
        super(Play2TimeitTest, cls).tearDownClass()

    def perform_work(self, framework, test_name):
        # get all of the variables
        servlet_name = 'Play2Test' + ":" + self.test_env.play2._config['default_app_name']
        report_type = 'FILE'
        summary = True
        concurrency = '200'
        iter_count = '10000'
        errors = -1
        path = '/hello?name=BobAnonymous&repeat=100&color=green'
        url = self.test_env.play2.get_url(path)
        
        for i in range(50):  # Ensure the app is loaded...
            assert self.test_env.play2.get_path(path).status == 200
        
        args = ['ab', '-k', '-r', '-c', concurrency, '-n', iter_count, url]
        
        childfhs = { 'stdout' : subprocess.PIPE, 'stderr' : subprocess.PIPE}
        errors = None

        for i in range(50):  # Number of recovery attempts after errors
            proc = subprocess.Popen(args, **childfhs)
    
            proc_out = proc.communicate()  # Wait for it to finish execution
    
            lines = proc_out[0].decode("utf-8").split('\n')
            for line in lines:
                if(line.startswith('Failed requests:')):
                    errors = int(re.findall('[.\d]+', line)[0])
                if(line.startswith('Time taken for tests:')):
                    runtime = re.findall('[.\d]+', line)[0]
                if(line.startswith('Requests per second:')):
                    rps = re.findall('[.\d]+', line)[0]
                if(line.startswith('  95%')):
                    ntile = re.findall('95%\s+([.\d]+)', line)[0]

            if(errors is None or int(iter_count) / 2 < errors):
                pass  # try again...
            else:
                break  # run was successful

        time.sleep(5)
        self.test_env.play2.shutdown()
    
        if(errors is None):
            print("ERROR:")
            print(proc_out[0].decode("utf-8"))
            print(proc_out[1].decode("utf-8"))
            assert False
        self.assertGreater(int(iter_count) / 2, errors, 'Too many errors: ' + str(errors))
        
        global all_metrics 
        # all_metrics.add_metric(servlet_name + '_runtime', report_type, test_name, framework, runtime, iter_count, self.test_env.play2.config_name, self.test_env.play2.version, summary)
        # all_metrics.add_metric(servlet_name + '_rps', report_type, test_name, framework, rps, iter_count, self.test_env.play2.config_name, self.test_env.play2.version, summary)
        all_metrics.add_metric(servlet_name + '_95tile', report_type, test_name, framework, ntile, iter_count, self.test_env.play2.config_name, self.test_env.play2.version, summary)

    
# Run without the agent (agent enabled is false)
    @collector
    @java_agent(select={'version': 'master'})
    @java(select={'version' : 7})
    @play2(jvm_args=['-Dnewrelic.config.enabled=false'])
    def test_disabled(self):
         
        self.perform_work('Play2TimeitTest', 'disabled')
        
# Run with agent but custom methods are not traced
    @collector
    @java_agent
    @java(select={'version' : 7})
    @play2(jvm_args=['-Dnewrelic.config.log_level=info', '-Dnewrelic.config.agent_enabled=true', '-Dnewrelic.config.audit_mode=false'])
    def test_enabled(self):
        
        self.perform_work('Play2TimeitTest', 'enabled')

# Run with tracer naming disabled
    @collector
    @java_agent
    @java(select={'version' : 7})
    @play2(jvm_args=['-Dnewrelic.config.log_level=info', '-Dnewrelic.config.agent_enabled=true', '-Dnewrelic.config.audit_mode=false', '-Dnewrelic.config.transaction_tracer.stack_based_naming=false'])
    def test_enabled_tracer_naming_diabled(self):
         
        self.perform_work('Play2TimeitTest', 'enabled_logging')


if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
