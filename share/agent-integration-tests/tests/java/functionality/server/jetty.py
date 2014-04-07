#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer
import time

class JettyTest(TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty
    #@jetty(select={'version' : [6.1, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 9.01, 9.03]})
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
            self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/RumServlet', data=data, headers=headers, response_size=response_size))
        actual_html = self.test_env.jetty.get_html().replace(b'\r', b'').decode("utf-8")

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/RumServlet'),
             {'count': 1})
        self.assertMatchesPattern(actual_html, expected_html)


    def mobile_apm_base(self, *attrs):
        data = bytes('1234567890', 'utf-8')
        headers = { 'X-Queue-Start' : 't={}'.format(time.time()-50), 'X-NewRelic-ID' : TestCase.OBFUSCATED_CROSS_PROCESS_ID, 'Content-Length' : '10' }
        response_size = '10000'
        before_body = b'<html>\n<head>\n<title>test servlet 2</title>\n<style type="text/css">\nh1{text-align:center; background:#dddddd;color:#000000}\nbody{font-family:sans-serif, arial; font-weight:normal}\n</style>\n</head>\n<body>'
        body = b'0' * int(response_size)
        after_body = b'</body>\n</html>\n'
        expected_html = bytes(before_body + body + after_body)
        self.assertTrue(
            self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet2', data=data, headers=headers, response_size=response_size))
        actual_html = self.test_env.jetty.get_html().replace(b'\r', b'')

        self.assertEqual(expected_html, actual_html, "HTML response does not match")
        self.assertTrue(
            self.test_env.jetty.get_response_header('TEST_HEADER', regex="TEST_HEADER CONTENT", deobfuscate=False))

        regex = '\[\"{}\",\"WebTransaction\\\/Servlet\\\/TestServlet2\\\",[0-9][\d]*\.[\d]+,\d+.\d+,10\]'.format(CollectorHTTPServer.AGENT_CROSS_PROCESS_ID)
        self.assertTrue(
            self.test_env.jetty.get_response_header('X-NewRelic-App-Data', regex=regex, deobfuscate=True))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('ClientApplication/{}/all'.format(TestCase.CROSS_PROCESS_ID)),
             {'count': 1})
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet2'),
             {'count': 1})
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('HttpDispatcher'),
             {'count': 1})
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Servlet/com.nr.test.servlet.TestServlet2/service'),
             {'count': 1})
        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/TestServlet2'), *attrs)

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [6.1]})
    def test_mobile_apm_6(self):
        self.mobile_apm_base(
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
                'name' : 'Java/org.mortbay.jetty.HttpConnection$Output/write',
                'count' : 39
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [7.0, 7.1, 7.2, 7.3, 7.4, 7.5]})
    def test_mobile_apm_7(self):
        self.mobile_apm_base(
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
                'name' : 'Java/org.eclipse.jetty.server.HttpConnection$Output/write',
                'count' : 39
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [7.6, 8.1]})
    def test_mobile_apm_76(self):
        self.mobile_apm_base(
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
                'name' : 'Java/org.eclipse.jetty.server.AbstractHttpConnection$Output/write',
                'count' : 39
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [9.01, 9.03]})
    def test_mobile_apm_9(self):
        self.mobile_apm_base(
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
                'name' : 'Java/org.eclipse.jetty.server.HttpOutput/write',
                'count' : 39
            },
            {
                'name' : 'Java/org.eclipse.jetty.server.HttpConnection$Input/read',
                'count' : 11
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [9.11]})
    def test_mobile_apm_91(self):
        self.mobile_apm_base(
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
                'name' : 'Java/org.eclipse.jetty.websocket.server.WebSocketUpgradeFilter/doFilter',
                'count' : 1
            },
            {
                'name' : 'Java/org.eclipse.jetty.server.HttpOutput/write',
                'count' : 39
            },
            {
                'name' : 'Java/org.eclipse.jetty.server.HttpInputOverHTTP/read',
                'count' : 11
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty
    def test_custom_extension(self):
        self.assertTrue(
                        self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/CustomTestServlet'))

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('Java/com.nr.test.servlet.CustomTestServlet/customTestMethod'),
                                  { 'count' : 1 })

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('OtherTransaction/CUSTOM/metricOtherMethod'),
                                  { 'count' : 1 })


    def async_base(self, *attrs):
        self.assertTrue(
                        self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/AsyncServlet'))

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('OtherTransaction/Custom/com.nr.test.servlet.AsyncServlet$1/run'),
                                  { 'count' : 1 })
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/WebServletPath/AsyncServlet'),
                                  { 'count' : 1 })
        self.assertIterAttributes(
                                  self.test_env.collector.get_scoped_metrics('WebTransaction/WebServletPath/AsyncServlet'), *attrs)

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [8.0]})
    def test_async_80(self):
        self.async_base(  
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.AsyncServlet/service',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.AsyncServlet2/service',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet2/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/org.eclipse.jetty.server.HttpConnection$Output/write',
                                  'count' : 2
                                  })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [8.1]})
    def test_async_81(self):
        self.async_base(
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.AsyncServlet/service',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.AsyncServlet2/service',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet2/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/org.eclipse.jetty.server.AbstractHttpConnection$Output/write',
                                  'count' : 2
                                  })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [9.01,9.03]})
    def test_async_9(self):
        self.async_base(
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet/init',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
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
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet2/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/org.eclipse.jetty.server.HttpOutput/write',
                                  'count' : 2
                                  })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [9.11]})
    def test_async_91(self):
        self.async_base(
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet/init',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
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
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServlet2/doGet',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/org.eclipse.jetty.websocket.server.WebSocketUpgradeFilter/doFilter',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/org.eclipse.jetty.server.HttpOutput/write',
                                  'count' : 1
                                  })

    def async_complete_base(self, *attrs):
        self.assertTrue(
                        self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/AsyncServletComplete'))

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('OtherTransaction/Custom/com.nr.test.servlet.AsyncServletComplete$1/run'),
                                  { 'count' : 1 })

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/WebServletPath/AsyncServletComplete'),
                                  { 'count' : 1 })

        self.assertIterAttributes(
                                  self.test_env.collector.get_scoped_metrics('WebTransaction/WebServletPath/AsyncServletComplete'), *attrs)

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [8.0, 8.1]})
    def test_async_complete_8(self):
        self.async_complete_base(
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.AsyncServletComplete/service',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.AsyncServletComplete/doGet',
                                  'count' : 1
                                  })

    def continuations_base(self, *attrs):
        self.assertTrue(
                        self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/Jetty7ContinuationsServlet'))

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('OtherTransaction/Custom/com.nr.test.servlet.Jetty7ContinuationsServlet$1/run'),
                                  { 'count' : 1 })

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/Jetty7ContinuationsServlet'),
                                  { 'count' : 1 })
        self.assertIterAttributes(
                                  self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/Jetty7ContinuationsServlet'), *attrs)

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [7.5]})
    def test_continuations_7(self):
        self.continuations_base(
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.Jetty7ContinuationsServlet/init',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.Jetty7ContinuationsServlet/service',
                                  'count' : 2
                                  },
                                  {
                                  'name' : 'Java/org.eclipse.jetty.server.HttpConnection$Output/write',
                                  'count' : 2
                                  })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [8.1]})
    def test_continuations_8(self):
        self.continuations_base(
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.Jetty7ContinuationsServlet/init',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.Jetty7ContinuationsServlet/service',
                                  'count' : 2
                                  },
                                  {
                                  'name' : 'Java/org.eclipse.jetty.server.AbstractHttpConnection$Output/write',
                                  'count' : 2
                                  })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [6.1]})
    def test_continuations_6(self):
        self.assertTrue(
                        self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/Jetty6ContinuationsServlet'))
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('OtherTransaction/Custom/com.nr.test.servlet.Jetty6ContinuationsServlet$1/run'),
                                  { 'count' : 1 })
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/Jetty6ContinuationsServlet'),
                                  { 'count' : 1 })
    
        self.assertIterAttributes(
                                  self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/Jetty6ContinuationsServlet'),
                                  {
                                  'name' : 'AsyncProcessing',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Servlet/com.nr.test.servlet.Jetty6ContinuationsServlet/service',
                                  'count' : 2
                                  },
                                  {
                                  'name' : 'Java/com.nr.test.servlet.Jetty6ContinuationsServlet/init',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                                  'count' : 1
                                  },
                                  {
                                  'name' : 'Java/org.mortbay.jetty.HttpConnection$Output/write',
                                  'count' : 2
                                  })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version': [6.1]}, jvm_args = ['-Dnewrelic.config.log_level=finest', '-Xmx1024m'])
    def test_metric_61(self):
        self.assertTrue(self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))

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
            },
            {
                'name' : 'Java/org.mortbay.jetty.HttpConnection$Output/write'
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version': [7.6]}, jvm_args = ['-Dnewrelic.config.log_level=finest', '-Xmx1024m'])
    def test_metric_76(self):
        self.assertTrue(self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))

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
            },
            {
                'name' : 'Java/org.eclipse.jetty.server.AbstractHttpConnection$Output/write'
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [8.1]}, jvm_args = ['-Dnewrelic.config.log_level=finest', '-Xmx1024m'])
    #@jetty
    def test_metric_81(self):
        self.assertTrue(self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))

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
            },
            {
                'name' : 'Java/org.eclipse.jetty.server.AbstractHttpConnection$Output/write'
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [7.0,7.1,7.2,7.3,7.4,7.5,8.0]}, jvm_args = ['-Dnewrelic.config.log_level=finest', '-Xmx1024m'])
    #@jetty
    def test_metric(self):
        self.assertTrue(self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))

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
            },
            {
                'name' : 'Java/org.eclipse.jetty.server.HttpConnection$Output/write',
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [9.01,9.03]}, jvm_args = ['-Dnewrelic.config.log_level=finest', '-Xmx1024m'])
    #@jetty
    def test_metric_9x(self):
        self.assertTrue(self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))

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
            },
            {
                'name' : 'Java/org.eclipse.jetty.server.HttpOutput/write'
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version' : [9.11]}, jvm_args = ['-Dnewrelic.config.log_level=finest', '-Xmx1024m'])
    #@jetty
    def test_metric_911(self):
        self.assertTrue(self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))

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
            },
            {
                'name' : 'Java/org.eclipse.jetty.server.HttpOutput/write'
            },
            {
                'name' : 'Java/org.eclipse.jetty.websocket.server.WebSocketUpgradeFilter/doFilter'
            })


    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty
    def test_metric_unscoped(self):
        self.assertTrue(self.test_env.jetty.get_path_and_shutdown('/java_test_webapp/TestServlet'))    

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/TestServlet'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('HttpDispatcher'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Servlet/com.nr.test.servlet.TestServlet/service'),
            { 'count' : 1 })

        self.assertDictContainsSubset(
            self.aggregate_by(self.test_env.collector.get_scoped_metrics(), 'name', 'count'),
            self.aggregate_by(self.test_env.collector.get_unscoped_metrics(), 'name', 'count'),
        )

    def transaction_trace_base(self, metric_name, class_name):
        self.assertTrue(
            self.test_env.jetty.get_path_and_shutdown(
                '/java_test_webapp/TestServlet',
                sleep_milliseconds='2000'))

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
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            })
    
    # I duplicated the entire transaction_trace_base for Jetty 9.1.1 because they added a filter
    # so we get a transaction trace for doFilter. There must be a better way ... but since this
    # is 9.1-specific, it may not be that much of a maintenance headache, either.
    def transaction_trace_base91(self, metric_name, class_name):
        self.assertTrue(
            self.test_env.jetty.get_path_and_shutdown(
                '/java_test_webapp/TestServlet',
                sleep_milliseconds='2000'))

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
                'metric_name' : 'Java/org.eclipse.jetty.websocket.server.WebSocketUpgradeFilter/doFilter',
                'class_name'  : 'org.eclipse.jetty.websocket.server.WebSocketUpgradeFilter',
                'method_name' : 'doFilter'
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
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            },
            {
                'metric_name' : metric_name,
                'class_name'  : class_name,
                'method_name' : 'write'
            })
    
    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version': [6.1]}, jvm_args=['-Dnewrelic.config.transaction_tracer.transaction_threshold=1.0'])
    def test_transaction_trace_6(self):
        self.transaction_trace_base('Java/org.mortbay.jetty.HttpConnection$Output/write', 'org.mortbay.jetty.AbstractGenerator$Output')      

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version': [7.0, 7.1, 7.2,7.3, 7.4, 7.5]}, jvm_args=['-Dnewrelic.config.transaction_tracer.transaction_threshold=1.0'])
    def test_transaction_trace_7(self):
        self.transaction_trace_base('Java/org.eclipse.jetty.server.HttpConnection$Output/write', 'org.eclipse.jetty.server.HttpOutput')

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version': [7.6, 8.1]}, jvm_args=['-Dnewrelic.config.transaction_tracer.transaction_threshold=1.0'])
    def test_transaction_trace_76(self):
        self.transaction_trace_base('Java/org.eclipse.jetty.server.AbstractHttpConnection$Output/write', 'org.eclipse.jetty.server.HttpOutput')

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version': [9.01, 9.03]}, jvm_args=['-Dnewrelic.config.transaction_tracer.transaction_threshold=1.0'])
    def test_transaction_trace_9(self):
        self.transaction_trace_base('Java/org.eclipse.jetty.server.HttpOutput/write', 'org.eclipse.jetty.server.HttpOutput')

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty(select={'version': [9.11]}, jvm_args=['-Dnewrelic.config.transaction_tracer.transaction_threshold=1.0'])
    def test_transaction_trace_91(self):
        self.transaction_trace_base91('Java/org.eclipse.jetty.server.HttpOutput/write', 'org.eclipse.jetty.server.HttpOutput')

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty
    def test_module(self):
        self.assertTrue(
            self.test_env.jetty.get_path(
                '/java_test_webapp/TestServlet',
                sleep_milliseconds='2000'))

        self.assertStringEqual(self.test_env.collector.get_module_name(), 'Jars')

        self.assertGreater(len(self.test_env.collector.get_modules()), 10);

        self.assertIterAttributes(
            self.test_env.collector.get_modules('commons-httpclient-3.0.1.jar'),
            {
                'name'           : 'commons-httpclient-3.0.1.jar',
                'version'        : '3.0.1',
            })

        self.test_env.jetty.shutdown()

    @collector
    @java_agent
    @java
    @java_test_webapp
    @jetty
    #@jetty(select={'version' : [8.0]})
    def test_error(self):
        self.test_env.jetty.get_path_and_shutdown(
            '/java_test_webapp/TestServlet',
            status_code='500')

        self.assertIterAttributes(
            self.test_env.collector.get_errors(),
            {
                'path'           : 'WebTransaction/Servlet/TestServlet',
                'message'        : 'HttpServerError 500',
                'exception_type' : 'HttpServerError 500'
            })

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
