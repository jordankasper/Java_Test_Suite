#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer
import time

class GlassfishTest(TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish(jvm_args=['-Dnewrelic.config.auto_instrument=false'])
    def test_manual_rum(self):
        data = bytes('1234567890', 'utf-8')
        headers = { 'Content-Length' : '10' }
        response_size = '100'
        before_script1 = '<html>\n<head>\n<title>rum servlet</title>\n'
        script1 = "\n<script type=\"text/javascript\">window.NREUM||(NREUM={}),__nr_require=function a(b,c,d)</script>\n"
        after_script1 = '<style type="text/css">\nh1{text-align:center; background:#dddddd;color:#000000}\nbody{font-family:sans-serif, arial; font-weight:normal}\n</style>\n</head>\n<body>'
        body = '0' * int(response_size)
        script2 = '<script type="text/javascript">window.NREUM||(NREUM={});NREUM.info={"applicationID":"45047","applicationTime":.*?,"beacon":"staging-beacon-2.newrelic.com","queueTime":.*?,"licenseKey":"12345","transactionName":"OwwBMRwSCxgEGkVbXAJGMAAcBQkOEVZjR14\/DBETAhYR","agent":"js-agent.newrelic.com\nr-248.min.js","errorBeacon":"staging-jserror.newrelic.com"}</script>'
        end = '\n</body></html>\n'
        expected_html = before_script1 + script1 + after_script1 + body + script2 + end

        self.assertTrue(
            self.test_env.glassfish.get_path_and_shutdown('/java_test_webapp/RumServlet', data=data, headers=headers, response_size=response_size))
        actual_html = self.test_env.glassfish.get_html().replace(b'\r', b'').decode("utf-8")

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/RumServlet'),
             {'count': 1})
        self.assertMatchesPattern(actual_html, expected_html)

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish(select={'version' : 3.1})
    def test_mobile_apm_3(self):
        data = bytes('1234567890', 'utf-8')
        headers = { 'X-Queue-Start' : 't={}'.format(time.time()-50), 'X-NewRelic-ID' : TestCase.OBFUSCATED_CROSS_PROCESS_ID, 'Content-Length' : '10' }
        response_size = '10000'
        before_body = b'<html>\n<head>\n<title>test servlet 2</title>\n<style type="text/css">\nh1{text-align:center; background:#dddddd;color:#000000}\nbody{font-family:sans-serif, arial; font-weight:normal}\n</style>\n</head>\n<body>'
        body = b'0' * int(response_size)
        after_body = b'</body>\n</html>\n'
        expected_html = bytes(before_body + body + after_body)
        self.assertTrue(
            self.test_env.glassfish.get_path_and_shutdown('/java_test_webapp/TestServlet2', data=data, headers=headers, response_size=response_size))

        actual_html = self.test_env.glassfish.get_html().replace(b'\r', b'')

        self.assertEqual(expected_html, actual_html, "HTML response does not match")

        self.assertTrue(
            self.test_env.glassfish.get_response_header('TEST_HEADER', regex="TEST_HEADER CONTENT", deobfuscate=False))

        regex = '\[\"{}\",\"WebTransaction\\\/Servlet\\\/TestServlet2\\\",[0-9][\d]*\.[\d]+,\d+.\d+,10\]'.format(CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertTrue(
            self.test_env.glassfish.get_response_header('X-NewRelic-App-Data', regex=regex, deobfuscate=True))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('ClientApplication/{}/all'.format(TestCase.CROSS_PROCESS_ID)),
             {'count': 0},count=self.assertGreater)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet2'),
             {'count': 1})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('HttpDispatcher'),
             {'count': 0},count=self.assertGreater)

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/TestServlet2'),
            {
                'name' : 'Java/com.nr.test.servlet.TestServlet2/init',
                'count' : 2
            },
            {
                'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name' : 'Servlet/com.nr.test.servlet.TestServlet2/service',
                'count' : 1
            },
            {
                'name' : 'Java/org.apache.catalina.connector.CoyoteInputStream/read',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish(select={'version' : 4.0})
    def test_mobile_apm_4(self):
        data = bytes('1234567890', 'utf-8')
        headers = { 'X-Queue-Start' : 't={}'.format(time.time()-50), 'X-NewRelic-ID' : TestCase.OBFUSCATED_CROSS_PROCESS_ID, 'Content-Length' : '10' }
        response_size = '10000'
        before_body = b'<html>\n<head>\n<title>test servlet 2</title>\n<style type="text/css">\nh1{text-align:center; background:#dddddd;color:#000000}\nbody{font-family:sans-serif, arial; font-weight:normal}\n</style>\n</head>\n<body>'
        body = b'0' * int(response_size)
        after_body = b'</body>\n</html>\n'
        expected_html = bytes(before_body + body + after_body)
        self.assertTrue(
            self.test_env.glassfish.get_path_and_shutdown('/java_test_webapp/TestServlet2', data=data, headers=headers, response_size=response_size))

        actual_html = self.test_env.glassfish.get_html().replace(b'\r', b'')

        self.assertEqual(expected_html, actual_html, "HTML response does not match")

        self.assertTrue(
            self.test_env.glassfish.get_response_header('TEST_HEADER', regex="TEST_HEADER CONTENT", deobfuscate=False))

        regex = '\[\"{}\",\"WebTransaction\\\/Servlet\\\/TestServlet2\\\",[0-9][\d]*\.[\d]+,\d+.\d+,10\]'.format(CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        
        self.assertTrue(
            self.test_env.glassfish.get_response_header('X-NewRelic-App-Data', regex=regex, deobfuscate=True))
        
        
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('ClientApplication/{}/all'.format(TestCase.CROSS_PROCESS_ID)),
             {'count': 0},count=self.assertGreater)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet2'),
             {'count': 1})

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/TestServlet2'),
            {
                'name' : 'Java/com.nr.test.servlet.TestServlet2/init',
                'count' : 2
            },
            {
                'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name' : 'Servlet/com.nr.test.servlet.TestServlet2/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
#    @glassfish(jvm_args=['-Dnewrelic.config.log_level=finest'])
    @glassfish()
    def test_async(self):
        self.assertTrue(
                        self.test_env.glassfish.get_path_and_shutdown('/java_test_webapp/AsyncServlet'))
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('OtherTransaction/Custom/com.nr.test.servlet.AsyncServlet$1/run'),
                                  { 'count' : 1 })
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/WebServletPath/AsyncServlet'),
                                  { 'count' : 1 })
    
        self.assertIterAttributes(
                                  self.test_env.collector.get_scoped_metrics('WebTransaction/WebServletPath/AsyncServlet'),
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet/init',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.AsyncServlet/service',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet2/init',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.AsyncServlet2/service',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet2/doGet',
                                  'count' : 1
                                  })

    @collector
    @java_agent
    @java
    @java_test_webapp
#    @glassfish(select={'version' : 4.0})
    @glassfish
    def test_metric(self):
        self.assertTrue(self.test_env.glassfish.get_path_and_shutdown('/java_test_webapp/TestServlet'))

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/TestServlet'),
            {
                'name' : 'Java/com.nr.test.servlet.TestServlet/init',
                'count' : 2
            },
            {
                'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name' : 'Servlet/com.nr.test.servlet.TestServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish(select={'version' : 3.1})
    def test_metric_unscoped_3(self):
        self.assertTrue(self.test_env.glassfish.get_path_and_shutdown('/java_test_webapp/TestServlet'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('HttpDispatcher'),
             {'count': 0},count=self.assertGreater)

        self.assertDictContainsSubset(
            self.aggregate_by(self.test_env.collector.get_scoped_metrics(), 'name', 'count'),
            self.aggregate_by(self.test_env.collector.get_unscoped_metrics(), 'name', 'count'),
        )

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish(select={'version' : 4.0})
    def test_metric_unscoped_4(self):
        self.assertTrue(self.test_env.glassfish.get_path_and_shutdown('/java_test_webapp/TestServlet'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet'),
            { 'count' : 1 })

        self.assertDictContainsSubset(
            self.aggregate_by(self.test_env.collector.get_scoped_metrics(), 'name', 'count'),
            self.aggregate_by(self.test_env.collector.get_unscoped_metrics(), 'name', 'count'),
        )

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish
    def test_transaction_trace(self):
        '''To guarantee a transaction trace, the sleep time must exceed the duration of the 'WebTransaction/RestWebService/{command:.*} (POST)' transactions created by the asadmin commnands'''
        self.assertTrue(
            self.test_env.glassfish.get_path_and_shutdown(
                '/java_test_webapp/TestServlet',
                sleep_milliseconds='30000'))

        tts = self.test_env.collector.get_transaction_traces('WebTransaction/Servlet/TestServlet')

        self.assertIterAttributes(
            tts,
            {
                'uri'  : '/java_test_webapp/TestServlet',
                'name' : 'WebTransaction/Servlet/TestServlet'
            })

        self.assertIterAttributes(
            tts[0].segments,
            {
                'metric_name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'class_name'  : 'javax.servlet.ServletRequestListener',
                'method_name' : 'requestInitialized'
            },
            {
                'metric_name' : 'Java/com.nr.test.servlet.TestServlet/init',
                'class_name'  : 'com.nr.test.servlet.TestServlet',
                'method_name' : 'init'
            },
            {
                'metric_name' : 'Java/com.nr.test.servlet.TestServlet/init',
                'class_name'  : 'javax.servlet.GenericServlet',
                'method_name' : 'init'
            },
            {
                'metric_name' : 'Servlet/com.nr.test.servlet.TestServlet/service',
                'class_name'  : 'javax.servlet.http.HttpServlet',
                'method_name' : 'service'
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish
    def test_module(self):
        try:
            self.assertTrue(
                self.test_env.glassfish.get_path(
                    '/java_test_webapp/TestServlet',
                    sleep_milliseconds='2000'))
    
            self.assertStringEqual(self.test_env.collector.get_module_name(), 'Jars')
    
            self.assertIterAttributes(
                self.test_env.collector.get_modules('commons-httpclient-3.0.1.jar'),
                {
                    'name'           : 'commons-httpclient-3.0.1.jar'
                })
    
            self.assertIterAttributes(
                self.test_env.collector.get_modules('commons-logging-1.0.3.jar'),
                {
                    'name'           : 'commons-logging-1.0.3.jar'
                })
    
            self.assertIterAttributes(
                self.test_env.collector.get_modules('mysql-connector-java-5.1.6.jar'),
                {
                    'name'           : 'mysql-connector-java-5.1.6.jar'
                })
    
            self.assertIterAttributes(
                self.test_env.collector.get_modules('jetty-continuation-7.5.4.v20111024.jar'),
                {
                    'name'           : 'jetty-continuation-7.5.4.v20111024.jar'
                })
        finally:
            self.test_env.glassfish.shutdown()

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish
    def test_error(self):
        self.test_env.glassfish.get_path_and_shutdown(
            '/java_test_webapp/TestServlet',
            status_code='500')

        self.assertIterAttributes(
            self.test_env.collector.get_errors(),
            {
                'path'           : 'WebTransaction/Servlet/TestServlet',
                'message'        : 'HttpServerError 500',
                'exception_type' : 'HttpServerError 500'
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @glassfish
    def test_transaction_rename(self):
        self.assertTrue(self.test_env.glassfish.get_path_and_shutdown(
                '/java_test_webapp/NewRelicApiServlet',
                api='setTransactionName',
                api_args='NewRelicApiServlet/SOMETHING/ETC'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Custom/NewRelicApiServlet/SOMETHING/ETC'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Custom/NewRelicApiServlet/SOMETHING/ETC'),
            {
                'name' : 'Java/com.nr.test.servlet.NewRelicApiServlet/init',
                'count' : 2
            },
            {
                'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name' : 'Servlet/com.nr.test.servlet.NewRelicApiServlet/service',
                'count' : 1
            })

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
