#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import collector
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer
import time

class PlayTest(TestCase):

    @collector
    @java_agent
    @java
    @play
    def test_mobile_apm(self):
         
        currentTime = int(round(time.time() * 1000))
        headers = { 'X-Queue-Start' : 't='+ str(currentTime), 'X-NewRelic-ID' : TestCase.OBFUSCATED_CROSS_PROCESS_ID.decode('utf-8')}
        self.assertTrue(
            self.test_env.play.get_path_and_shutdown('/', data=None, headers=headers))

        regex = '\[\"{}\",\"WebTransaction\\\/PlayTemplate\\\/Forums\\\/index.html\\\",[0123456789]\d*.\d+,\d+.\d+,-1\]'.format(CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertTrue(
            self.test_env.play.get_response_header('X-NewRelic-App-Data', regex=regex, deobfuscate=True))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('ClientApplication/{}/all'.format(TestCase.CROSS_PROCESS_ID)),
             {'count': 1})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayTemplate/Forums/index.html'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics(scope='WebTransaction/PlayTemplate/Forums/index.html'),
            {
                'name'     : 'Controller.renderTemplate/Forums/index.html',
                'count'    : 1,
                'min_time' : 0
            },
            {
                'name'     : 'Database/ResultSet',
                'count'    : 7,
                'min_time' : 0
            },
            {
                'name'     : 'Database/forum/select',
                'count'    : 1,
                'min_time' : 0
            },
            {
                'name'     : 'Database/post/select',
                'count'    : 1,
                'min_time' : 0
            },
            {
                'name'     : 'Database/topic/select',
                'count'    : 1,
                'min_time' : 0
            },
            {
                'name'     : 'RequestDispatcher',
                'count'    : 1,
                'min_time' : 0
            },
            min_time=self.assertGreater)

    @collector
    @java_agent
    @java
    @play
    def test_metric(self):
        self.assertTrue(self.test_env.play.get_path_and_shutdown('/'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayTemplate/Forums/index.html'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics(scope='WebTransaction/PlayTemplate/Forums/index.html'),
            {
                'name'     : 'Controller.renderTemplate/Forums/index.html',
                'count'    : 1,
                'min_time' : 0
            },
            {
                'name'     : 'Database/ResultSet',
                'count'    : 7,
                'min_time' : 0
            },
            {
                'name'     : 'Database/forum/select',
                'count'    : 1,
                'min_time' : 0
            },
            {
                'name'     : 'Database/post/select',
                'count'    : 1,
                'min_time' : 0
            },
            {
                'name'     : 'Database/topic/select',
                'count'    : 1,
                'min_time' : 0
            },
            {
                'name'     : 'RequestDispatcher',
                'count'    : 1,
                'min_time' : 0
            },
            min_time=self.assertGreater)

    @collector
    @java_agent
    @java
    @play
    def test_transaction_trace(self):
        self.assertTrue(self.test_env.play.get_path_and_shutdown('/'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayTemplate/Forums/index.html'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        tts = self.test_env.collector.get_transaction_traces(
            'WebTransaction/PlayTemplate/Forums/index.html')

        self.assertIterAttributes(
            tts,
            {
                'uri'  : '/',
                'name' : 'WebTransaction/PlayTemplate/Forums/index.html'
            })

        self.assertIterAttributes(
            tts[0].segments,
            {
                'metric_name' : 'RequestDispatcher/play.mvc.ActionInvoker/invoke',
                'class_name'  : 'play.mvc.ActionInvoker',
                'method_name' : 'invoke'
            },
            {
                'metric_name' : 'Database/forum/select',
                'class_name'  : 'org.h2.jdbc.JdbcPreparedStatement',
                'method_name' : 'executeQuery'
            },
            {
                'metric_name' : 'Database/topic/select',
                'class_name'  : 'org.h2.jdbc.JdbcPreparedStatement',
                'method_name' : 'executeQuery'
            },
            {
                'metric_name' : 'Database/post/select',
                'class_name'  : 'org.h2.jdbc.JdbcPreparedStatement',
                'method_name' : 'executeQuery'
            },
            {
                'metric_name' : 'Controller.renderTemplate/Forums/index.html',
                'class_name'  : 'play.mvc.Controller',
                'method_name' : 'renderTemplate'
            })

    @collector
    @java_agent
    @java
    @play(custom={'app' : 'samples-and-tests/asynctest'})
    def test_async_trace(self):
        self.assertTrue(self.test_env.play.get_path_and_shutdown('/asynctest1'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayTemplate/AsyncTest1/index.html'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        tts = self.test_env.collector.get_transaction_traces(
            'WebTransaction/PlayTemplate/AsyncTest1/index.html')

        self.assertIterAttributes(
            tts,
            {
                'uri'  : '/asynctest1',
                'name' : 'WebTransaction/PlayTemplate/AsyncTest1/index.html'
            })

        self.assertIterAttributes(
            tts[0].segments,
            {
                'metric_name' : 'RequestDispatcher/play.mvc.ActionInvoker/invoke',
                'class_name'  : 'play.mvc.ActionInvoker',
                'method_name' : 'invoke'
            },
            {
                'metric_name' : 'Controller.await',
                'class_name'  : 'play.mvc.Controller',
                'method_name' : 'await'
            },
            {
                'metric_name' : 'Custom/controllers.AsyncTest1/method4',
                'class_name'  : 'controllers.AsyncTest1',
                'method_name' : 'method4'
            },
            {
                'metric_name' : 'Controller.renderTemplate/AsyncTest1/index.html',
                'class_name'  : 'play.mvc.Controller',
                'method_name' : 'renderTemplate'
            })

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
