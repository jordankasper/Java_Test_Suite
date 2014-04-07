#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
import newrelic.agenttest.unittest
from newrelic.agenttest.unittest import TestCase
from newrelic.collector import CollectorHTTPServer
from newrelic.agenttest import obfuscator

class ExternalTest(newrelic.agenttest.unittest.TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_http_client_3(self):
        url = 'http://www.apache.org'
        method = 'HttpClient_3'
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/ExternalCallServlet',
                url=url, method=method))
        
        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            {
                'name'  : 'External/www.apache.org/CommonsHttp',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.ExternalCallServlet/init',
                'count' : 2,
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.ExternalCallServlet/service',
                'count' : 1
            })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/www.apache.org/CommonsHttp'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/all'),
            { 'count' : 1 })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_http_client_4(self):
        url = 'http://www.apache.org'
        method = 'HttpClient_4'
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/ExternalCallServlet',
                url=url, method=method))
        
        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            {
                'name'  : 'External/www.apache.org/CommonsHttp',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.ExternalCallServlet/init',
                'count' : 2,
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.ExternalCallServlet/service',
                'count' : 1
            })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/www.apache.org/CommonsHttp'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/all'),
            { 'count' : 1 })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_http_url_connection(self):
        url = 'http://www.apache.org'
        method = 'HttpURLConnection'
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/ExternalCallServlet',
                url=url, method=method))
        
        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            {
                'name'  : 'External/www.apache.org/HttpURLConnection',
                'count' : 2
            },
            {
                'name'  : 'Java/com.nr.test.servlet.ExternalCallServlet/init',
                'count' : 2,
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.ExternalCallServlet/service',
                'count' : 1
            })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/www.apache.org/HttpURLConnection'),
            { 'count' : 2 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/all'),
            { 'count' : 2 })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_cross_application_http_client_3(self):
        host = 'localhost'
        url = 'http://{}:{}/java_test_webapp/TestServlet?sleep_milliseconds=2000'.format(host, self.test_env.tomcat.get_port())
        method = 'HttpClient_3'
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/ExternalCallServlet',
                url=url, method=method))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet'),
             {'count': 1})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('HttpDispatcher'),
             {'count': 2})
        
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Servlet/com.nr.test.servlet.TestServlet/service'),
             {'count': 1})

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

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            { 'count' : 1 })

        cross_process_metric = 'ExternalApp/{}/{}/all'.format(host, CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(cross_process_metric),
            { 'count' : 1 })

        transaction_metric = 'ExternalTransaction/{}/{}/{}'.format(host, CollectorHTTPServer.AGENT_CROSS_PROCESS_ID, 'WebTransaction/Servlet/TestServlet')
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(transaction_metric),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/all'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/allWeb'),
            { 'count' : 1 })

        external_host_metric = 'External/{}/all'.format(host)
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(external_host_metric),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            {
                'name'  : transaction_metric,
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.ExternalCallServlet/init',
                'count' : 2,
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.ExternalCallServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_cross_application_http_client_4(self):
        host = 'localhost'
        url = 'http://{}:{}/java_test_webapp/TestServlet'.format(host, self.test_env.tomcat.get_port())
        method = 'HttpClient_4'
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/ExternalCallServlet',
                url=url, method=method))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet'),
             {'count': 1})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('HttpDispatcher'),
             {'count': 2})
        
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Servlet/com.nr.test.servlet.TestServlet/service'),
             {'count': 1})

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

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            { 'count' : 1 })

        cross_process_metric = 'ExternalApp/{}/{}/all'.format(host, CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(cross_process_metric),
            { 'count' : 1 })

        transaction_metric = 'ExternalTransaction/{}/{}/{}'.format(host, CollectorHTTPServer.AGENT_CROSS_PROCESS_ID, 'WebTransaction/Servlet/TestServlet')
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(transaction_metric),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/all'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/allWeb'),
            { 'count' : 1 })

        external_host_metric = 'External/{}/all'.format(host)
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(external_host_metric),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            {
                'name'  : transaction_metric,
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.ExternalCallServlet/init',
                'count' : 2,
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.ExternalCallServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_cross_application_http_url_connection(self):
        host = 'localhost'
        url = 'http://{}:{}/java_test_webapp/TestServlet2?sleep_milliseconds=2000'.format(host, self.test_env.tomcat.get_port())
        method = 'HttpURLConnection'
        sleep = 'sleep_milliseconds=2000'
        response_size = '10000'
        before_body = b'<html>\n<head>\n<title>test servlet 2</title>\n<style type="text/css">\nh1{text-align:center; background:#dddddd;color:#000000}\nbody{font-family:sans-serif, arial; font-weight:normal}\n</style>\n</head>\n<body>'
        body = b'0' * int(response_size)
        after_body = b'</body>\n</html>\n'
        expected_html = bytes(before_body + body + after_body)
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/ExternalCallServlet',
                url=url, method=method, sleep=sleep, response_size=response_size))
 
        actual_html = self.test_env.tomcat.get_html().replace(b'\r', b'')

        self.assertEqual(expected_html, actual_html, "HTML response does not match")

        self.assertTrue(
            self.test_env.tomcat.get_response_header('TEST_HEADER', regex="TEST_HEADER CONTENT", deobfuscate=False))

        regex = '\[\"{}\",\"WebTransaction\\\/Servlet\\\/TestServlet2\\\",0.0,\d+.\d+,-1,\"[a-f,0-9]+\"\]'.format(CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertTrue(
            self.test_env.tomcat.get_response_header('X-NewRelic-App-Data', regex=regex, deobfuscate=True))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet2'),
             {'count': 1})
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('HttpDispatcher'),
             {'count': 2})
        
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Servlet/com.nr.test.servlet.TestServlet2/service'),
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
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            { 'count' : 1 })
 
        cross_process_metric = 'ExternalApp/{}/{}/all'.format(host, CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(cross_process_metric),
            { 'count' : 1 })
 
        transaction_metric = 'ExternalTransaction/{}/{}/{}'.format(host, CollectorHTTPServer.AGENT_CROSS_PROCESS_ID, 'WebTransaction/Servlet/TestServlet2')
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(transaction_metric),
            { 'count' : 1 })
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/all'),
            { 'count' : 2 })
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('External/allWeb'),
            { 'count' : 2 })
 
        external_host_metric = 'External/{}/all'.format(host)
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics(external_host_metric),
            { 'count' : 2 })
 
        self.assertIterAttributes(self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/ExternalCallServlet'),
            {
                'name'  : 'External/localhost/HttpURLConnection',
                'count' : 1,
            },
            {
                'name'  : transaction_metric,
                'count' : 1,
            },
            {
                'name'  : 'Java/com.nr.test.servlet.ExternalCallServlet/init',
                'count' : 2,
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.ExternalCallServlet/service',
                'count' : 1
            })
 
    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_cross_application_transaction_trace_outbound(self):
        host = 'localhost'
        url = 'http://{}:{}/java_test_webapp/TestServlet'.format(host, self.test_env.tomcat.get_port())
        method = 'HttpClient_4'
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/ExternalCallServlet',
                url=url, method=method, sleep_milliseconds='2000'))

        tts = self.test_env.collector.get_transaction_traces('WebTransaction/Servlet/ExternalCallServlet')
        tt = tts[0];

        self.assertIsNone(tt.custom_params.get('client_cross_process_id'))
        self.assertIsNone(tt.custom_params.get('referring_transaction_guid'))
        self.assertEqual('/java_test_webapp/ExternalCallServlet', tt.uri)
        self.assertIsNotNone(tt.guid)
        self.assertEqual('WebTransaction/Servlet/ExternalCallServlet', tt.name)
        self.assertFalse(tt.force_persist)

        external_metric_name = 'ExternalTransaction/localhost/{}/WebTransaction/Servlet/TestServlet'.format(CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertIterAttributes(
            tt.segments,
            {
                'metric_name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'class_name'  : 'javax.servlet.ServletRequestListener',
                'method_name' : 'requestInitialized'
            },
            {
                'metric_name' : 'Java/com.nr.test.servlet.ExternalCallServlet/init',
                'class_name'  : 'com.nr.test.servlet.ExternalCallServlet',
                'method_name' : 'init'
            },
            {
                'metric_name' : 'Java/com.nr.test.servlet.ExternalCallServlet/init',
                'class_name'  : 'javax.servlet.GenericServlet',
                'method_name' : 'init'
            },
            {
                'metric_name' : 'Servlet/com.nr.test.servlet.ExternalCallServlet/service',
                'class_name'  : 'javax.servlet.http.HttpServlet',
                'method_name' : 'service'
            },
            {
                'metric_name' : external_metric_name,
                'class_name'  : 'org.apache.http.impl.client.AbstractHttpClient',
                'method_name' : 'execute'
            })

        self.assertEqual(url, tt.segments[4].params.get('uri'))
        self.assertIsNotNone(tt.segments[4].params.get('transaction_guid'))

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_cross_application_transaction_trace_inbound(self):
        guid = 'ee8e5ef1a374c0ec'
        transaction_header = obfuscator.obfuscate('[\"{}\",false]'.format(guid))
        headers = { 'X-NewRelic-Transaction' : transaction_header, 'X-NewRelic-ID' : TestCase.OBFUSCATED_CROSS_PROCESS_ID }
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/TestServlet',
                sleep_milliseconds='2000', headers=headers))
        regex = '\[\"{}\",\"WebTransaction\\\/Servlet\\\/TestServlet\\\",0.0,\d+.\d+,-1,\"[0-9,a-f]+\"\]'.format(CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertTrue(
            self.test_env.tomcat.get_response_header('X-NewRelic-App-Data', regex=regex, deobfuscate=True))

        tts = self.test_env.collector.get_transaction_traces('WebTransaction/Servlet/TestServlet')
        tt = tts[0];

        self.assertEqual(TestCase.CROSS_PROCESS_ID, tt.custom_params.get('client_cross_process_id'))
        self.assertEqual(guid, tt.custom_params.get('referring_transaction_guid'))
        self.assertEqual('/java_test_webapp/TestServlet', tt.uri)
        self.assertIsNotNone(tt.guid)
        self.assertEqual('WebTransaction/Servlet/TestServlet', tt.name)
        self.assertFalse(tt.force_persist)

        self.assertIterAttributes(
            tt.segments,
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

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
