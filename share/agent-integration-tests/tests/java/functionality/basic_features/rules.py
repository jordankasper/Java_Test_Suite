#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
import newrelic.agenttest.unittest

class RulesTest(newrelic.agenttest.unittest.TestCase):

    @collector(
        custom={
            'connect_options' : {
                'transaction_name_rules' : [{
                    'eval_order'       : 2,
                    'each_segment'     : False,
                    'match_expression' : r'^WebTransaction/Custom/java_test_webapp/NewRelicApiServlet/SOMETHING/(.*)$',
                    'replacement'      : r'WebTransaction/NewRelicApiServlet/SOMETHING_ELSE/\1',
                    'terminate_chain'  : True,
                    'replace_all'      : False,
                    'ignore'           : False
                }],
            }
        }
    )
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_transaction_rename(self):
        self.assertTrue(self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/NewRelicApiServlet',
                api='setTransactionName',
                api_args='/java_test_webapp/NewRelicApiServlet/SOMETHING/ETC'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/NewRelicApiServlet/SOMETHING_ELSE/ETC'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/NewRelicApiServlet/SOMETHING_ELSE/ETC'),
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

    @collector(
        custom={
            'connect_options' : {
                'metric_name_rules' : [{
                    'eval_order'       : 2,
                    'each_segment'     : False,
                    'match_expression' : r'^Custom/RequestTime/(.*)$',
                    'replacement'      : r'Custom/\1/RequestTime',
                    'terminate_chain'  : True,
                    'replace_all'      : False,
                    'ignore'           : False
                }]
            }
        }
    )
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_metric_rename(self):
        self.assertTrue(self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/NewRelicApiServlet',
                api='recordMetric',
                api_args='Custom/RequestTime/Time,1'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/Servlet/NewRelicApiServlet'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Custom/Time/RequestTime'),
            {
                'name' : 'Custom/Time/RequestTime',
                'count' : 1
            })

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
