#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
import newrelic.agenttest.unittest
from newrelic.agenttest import obfuscator

class JMSTest(newrelic.agenttest.unittest.TestCase):

    '''
    The JMSServlet inserts properties into the JMS messages it sends. The Agent transmits these to the Collector
    if the appropriate configuration properties are set. We set these using sysprops via an annotation below.
    Here, we check the properties.
    '''
    def check_message_properties_present(self):
        tts = self.test_env.collector.get_transaction_traces('OtherTransaction/Message/JMS/Queue/Named/AitTestQueue')
        self.assertNull(tts[0].request_params.get('IgnoredShouldNotAppearInTestResult'))
        self.assertEqual(tts[0].request_params.get('Int43'), '43')
        self.assertEqual(tts[0].request_params.get('StringHello'), 'Hello')
        self.assertEqual(tts[0].request_params.get('Float42dot4'), '42.4')
        self.assertEqual(tts[0].request_params.get('Double42dot42'), '42.42')
        self.assertEqual(tts[0].request_params.get('Byte42'), '42')
        self.assertEqual(tts[0].request_params.get('BooleanTrue'), 'true')
        
    '''
    And here, we check the properties are absent, as would be expected when the config property to enable them is not set.
    '''
    def check_message_properties_absent(self):
        tts = self.test_env.collector.get_transaction_traces('OtherTransaction/Message/JMS/Queue/Named/AitTestQueue')
        self.assertNull(tts[0].request_params.get('IgnoredShouldNotAppearInTestResult'))
        self.assertNull(tts[0].request_params.get('Int43'))
        self.assertNull(tts[0].request_params.get('StringHello'))
        self.assertNull(tts[0].request_params.get('Float42dot4'))
        self.assertNull(tts[0].request_params.get('Double42dot42'))
        self.assertNull(tts[0].request_params.get('Byte42'))
        self.assertNull(tts[0].request_params.get('BooleanTrue'))
        
    @collector
    @java_agent
    @java(select={'version' : 7})
    @java_test_webapp
    @activemq
    @tomcat(select={'version' : 7}, jvm_args=[ '-Dnewrelic.config.capture_messaging_params=true -Dnewrelic.config.ignored_messaging_params=IgnoredShouldNotAppearInTestResult' ])
    def test_simple_activemq(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/JMSServlet', provider='activemq'))
        self.assertInstrumentation({'jms-1.1': True, 'servlet-2.4':True})
        self.check_message_properties_present()
        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('OtherTransaction/Message/JMS/Queue/Named/AitTestQueue'),
            {
                'name'  : 'Java/org.apache.activemq.ActiveMQMessageProducer/send',
                'count' : 1
            },
            {
                'name'  : 'MessageBroker/JMS/Queue/Consume/Named/AitTestQueue',
                'count' : 1
            },
            {
                'name'  : 'MessageBroker/JMS/Queue/Produce/Temp',
                'count' : 1
            })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/JMSServlet'),
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'MessageBroker/JMS/Queue/Consume/Temp',
                'count' : 1
            },
            {
                'name'  : 'MessageBroker/JMS/Queue/Produce/Named/AitTestQueue',
                'count' : 1
            },
            {
                'name'  : 'Java/org.apache.activemq.ActiveMQMessageProducer/send',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.JMSServlet/service',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.JMSServlet/init',
                'count' : 2
            })

        # Validate Front-end CAT Metrics
        webTT = self.test_env.collector.get_transaction_traces('WebTransaction/Servlet/JMSServlet')[0]
        self.assertIsNotNone(webTT.guid)
        self.assertIsNone(webTT.custom_params.get('referring_transaction_guid'))
        self.assertIsNone(webTT.custom_params.get('client_cross_process_id'))
        self.assertEqual('/java_test_webapp/JMSServlet', webTT.uri)

        self.assertIsNotNone(webTT.segments[6].params.get('transaction_guid'))

        self.assertIterAttributes(
            webTT.segments,
            {
                'metric_name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'class_name'  : 'javax.servlet.ServletRequestListener',
                'method_name' : 'requestInitialized'
            },
            {
                'metric_name' : 'Java/com.nr.test.servlet.JMSServlet/init',
                'class_name'  : 'com.nr.test.servlet.TestServlet',
                'method_name' : 'init'
            },
            {
                'metric_name' : 'Java/com.nr.test.servlet.JMSServlet/init',
                'class_name'  : 'javax.servlet.GenericServlet',
                'method_name' : 'init'
            },
            {
                'metric_name' : 'Servlet/com.nr.test.servlet.JMSServlet/service',
                'class_name'  : 'javax.servlet.http.HttpServlet',
                'method_name' : 'service'
            },
            {
                'metric_name' : 'MessageBroker/JMS/Queue/Produce/Named/AitTestQueue',
                'class_name'  : 'org.apache.activemq.ActiveMQMessageProducerSupport',
                'method_name' : 'send'
            },
            {
                'metric_name' : 'Java/org.apache.activemq.ActiveMQMessageProducer/send',
                'class_name'  : 'org.apache.activemq.ActiveMQMessageProducer',
                'method_name' : 'send'
            },
            {
                'metric_name' : 'MessageBroker/JMS/Queue/Consume/Temp',
                'class_name'  : 'org.apache.activemq.ActiveMQMessageConsumer',
                'method_name' : 'receive'
            })
        
        # Validate Back-end CAT Metrics
        otherTT = self.test_env.collector.get_transaction_traces('OtherTransaction/Message/JMS/Queue/Named/AitTestQueue')[0]
        self.assertIsNotNone(otherTT.guid)

        self.assertIsNotNone(otherTT.request_params.get('NewRelicID'))
        otherReqTxObf = otherTT.request_params.get('NewRelicTransaction')
        otherReqTx = obfuscator.deobfuscate(otherReqTxObf)
        self.assertTrue(webTT.guid in otherReqTx)  # Incoming header should contain front-end's guid

        otherReferrer = otherTT.custom_params.get('referring_transaction_guid')
        self.assertEqual(webTT.guid, otherReferrer)  # Back-end should reference the front-end's guid
        self.assertIsNotNone(otherTT.custom_params.get('client_cross_process_id'))
        
        self.assertEqual('Java/com.nr.test.servlet.JMSServlet$Server/onMessage', otherTT.uri)
        
        self.assertIterAttributes(
            otherTT.segments,
            {
                'metric_name' : 'MessageBroker/JMS/Queue/Consume/Named/AitTestQueue',
                'class_name'  : 'com.nr.test.servlet.JMSServlet$Server',
                'method_name' : 'onMessage'
            },
            {
                'metric_name' : 'MessageBroker/JMS/Queue/Produce/Temp',
                'class_name'  : 'org.apache.activemq.ActiveMQMessageProducerSupport',
                'method_name' : 'send'
            },
            {
                'metric_name' : 'Java/org.apache.activemq.ActiveMQMessageProducer/send',
                'class_name'  : 'org.apache.activemq.ActiveMQMessageProducer',
                'method_name' : 'send'
            })

    @collector
    @java_agent
    @java(select={'version' : 7})
    @java_test_webapp
    @hornetq
    @tomcat(select={'version' : 7}, jvm_args=[ '-Dnewrelic.config.capture_messaging_params=true -Dnewrelic.config.ignored_messaging_params=IgnoredShouldNotAppearInTestResult' ])
    def test_simple_hornetq(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/JMSServlet', provider='hornetq'))
        self.assertInstrumentation({'jms-1.1': True, 'servlet-2.4':True})
        self.check_message_properties_present()
        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('OtherTransaction/Message/JMS/Queue/Named/AitTestQueue'),
            {
                'name'  : 'MessageBroker/JMS/Queue/Consume/Named/AitTestQueue',
                'count' : 1
            },
            {
                'name'  : 'MessageBroker/JMS/Queue/Produce/Temp',
                'count' : 1
            })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/JMSServlet'),
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'MessageBroker/JMS/Queue/Consume/Temp',
                'count' : 1
            },
            {
                'name'  : 'MessageBroker/JMS/Queue/Produce/Named/AitTestQueue',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.JMSServlet/service',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.JMSServlet/init',
                'count' : 2
            })

        # Validate Front-end CAT Metrics
        webTT = self.test_env.collector.get_transaction_traces('WebTransaction/Servlet/JMSServlet')[0]
        self.assertIsNotNone(webTT.guid)
        self.assertIsNone(webTT.custom_params.get('referring_transaction_guid'))
        self.assertIsNone(webTT.custom_params.get('client_cross_process_id'))
        self.assertEqual('/java_test_webapp/JMSServlet', webTT.uri)

        self.assertIsNotNone(webTT.segments[5].params.get('transaction_guid'))

        self.assertIterAttributes(
            webTT.segments,
            {
                'metric_name' : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'class_name'  : 'javax.servlet.ServletRequestListener',
                'method_name' : 'requestInitialized'
            },
            {
                'metric_name' : 'Java/com.nr.test.servlet.JMSServlet/init',
                'class_name'  : 'com.nr.test.servlet.TestServlet',
                'method_name' : 'init'
            },
            {
                'metric_name' : 'Java/com.nr.test.servlet.JMSServlet/init',
                'class_name'  : 'javax.servlet.GenericServlet',
                'method_name' : 'init'
            },
            {
                'metric_name' : 'Servlet/com.nr.test.servlet.JMSServlet/service',
                'class_name'  : 'javax.servlet.http.HttpServlet',
                'method_name' : 'service'
            },
            {
                'metric_name' : 'MessageBroker/JMS/Queue/Produce/Named/AitTestQueue',
                'class_name'  : 'org.hornetq.jms.client.HornetQMessageProducer',
                'method_name' : 'send'
            },
            {
                'metric_name' : 'MessageBroker/JMS/Queue/Consume/Temp',
                'class_name'  : 'org.hornetq.jms.client.HornetQMessageConsumer',
                'method_name' : 'receive'
            })
        
        # Validate Back-end CAT Metrics
        otherTT = self.test_env.collector.get_transaction_traces('OtherTransaction/Message/JMS/Queue/Named/AitTestQueue')[0]
        self.assertIsNotNone(otherTT.guid)

        self.assertIsNotNone(otherTT.request_params.get('NewRelicID'))
        otherReqTxObf = otherTT.request_params.get('NewRelicTransaction')
        otherReqTx = obfuscator.deobfuscate(otherReqTxObf)
        self.assertTrue(webTT.guid in otherReqTx)  # Incoming header should contain front-end's guid

        otherReferrer = otherTT.custom_params.get('referring_transaction_guid')
        self.assertEqual(webTT.guid, otherReferrer)  # Back-end should reference the front-end's guid
        self.assertIsNotNone(otherTT.custom_params.get('client_cross_process_id'))
        
        self.assertEqual('Java/com.nr.test.servlet.JMSServlet$Server/onMessage', otherTT.uri)
        
        self.assertIterAttributes(
            otherTT.segments,
            {
                'metric_name' : 'MessageBroker/JMS/Queue/Consume/Named/AitTestQueue',
                'class_name'  : 'com.nr.test.servlet.JMSServlet$Server',
                'method_name' : 'onMessage'
            },
            {
                'metric_name' : 'MessageBroker/JMS/Queue/Produce/Temp',
                'class_name'  : 'org.hornetq.jms.client.HornetQMessageProducer',
                'method_name' : 'send'
            })

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
