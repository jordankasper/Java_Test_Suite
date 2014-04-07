#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
import newrelic.agenttest.unittest

class DBTest(newrelic.agenttest.unittest.TestCase):

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_select_mysql(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/DBServlet',
                sql='select test_column from test_table',engine='mysql'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/all'),
            { 'count' : 1 })
  
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/test_table/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/DBServlet'),
            {
                'name'  : 'Database/ResultSet',
                'count' : 446
            },
            {
                'name'  : 'Database/test_table/select',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.DBServlet/init',
                'count' : 2
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.DBServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_mysql_prepared_threaded(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/DbThreadServlet',
                sql='select test_column from test_table',engine='mysql'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/all'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/test_table/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/DbThreadServlet'),
            {
                'name'  : 'Database/ResultSet',
                'count' : 9
            },
            {
                'name'  : 'Database/test_table/select',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.DbThreadServlet/init',
                'count' : 2
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.DbThreadServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    #, jvm_args = ['-Dnewrelic.config.log_level=finest'])
    def test_mysql_conn_threaded(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/DbConnThreadServlet',
                sql='select test_column from test_table',engine='mysql'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/all'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/test_table/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/DbConnThreadServlet'),
            {
                'name'  : 'Database/ResultSet',
                'count' : 9
            },
            {
                'name'  : 'Database/test_table/select',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.DbConnThreadServlet/init',
                'count' : 2
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.DbConnThreadServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_select_postgres(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/DBServlet',
               sql='select firstname,middlename,lastname,bool_flag from person',engine='postgres'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/all'),
            { 'count' : 1 })
  
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/person/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/DBServlet'),
            {
                'name'  : 'Database/ResultSet',
                'count' : 1
            },
            {
                'name'  : 'Database/person/select',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.DBServlet/init',
                'count' : 2
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.DBServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_postgres_prepared_threaded(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/DbThreadServlet',
               sql='select firstname,middlename,lastname,bool_flag from person',engine='postgres'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/all'),
            { 'count' : 1 })
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/person/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/DbThreadServlet'),
            {
                'name'  : 'Database/ResultSet',
                'count' : 1
            },
            {
                'name'  : 'Database/person/select',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.DbThreadServlet/init',
                'count' : 2
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.DbThreadServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_postgres_conn_threaded(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/DbConnThreadServlet',
               sql='select firstname,middlename,lastname,bool_flag from person',engine='postgres'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/all'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/person/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/DbConnThreadServlet'),
            {
                'name'  : 'Database/ResultSet',
                'count' : 1
            },
            {
                'name'  : 'Database/person/select',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.DbConnThreadServlet/init',
                'count' : 2
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.DbConnThreadServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_select_oracle(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown(
                '/java_test_webapp/DBServlet',
                sql='select firstname,middlename,lastname, bool_flag from person',engine='oracle'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/all'),
            { 'count' : 1 })
  
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Database/person/select'),
            { 'count' : 1 })

        self.assertIterAttributes(
            self.test_env.collector.get_scoped_metrics('WebTransaction/Servlet/DBServlet'),
           {
                'name'  : 'Database/ResultSet',
                'count' : 6
            },
            {
                'name'  : 'Database/person/select',
                'count' : 1
            },
            {
                'name'  : 'Java/com.nr.test.servlet.DBServlet/init',
                'count' : 2
            },
            {
                'name'  : 'Java/javax.servlet.ServletRequestListener/requestInitialized',
                'count' : 1
            },
            {
                'name'  : 'Servlet/com.nr.test.servlet.DBServlet/service',
                'count' : 1
            })

    @collector
    @java_agent
    @java
    @java_test_webapp
    @tomcat(select={'version' : 7})
    def test_sql_trace(self):
        try:
            self.assertTrue(
                self.test_env.tomcat.get_path(
                    '/java_test_webapp/DBServlet',
                    sql='select count(*) from test_table having sleep(1)', engine='mysql'))
    
            self.assertIterAttributes(
                self.test_env.collector.get_sql_traces('Database/test_table/select'),
                {
                    'uri'            : '/java_test_webapp/DBServlet',
                    'fe_metric_name' : 'WebTransaction/Servlet/DBServlet',
                    'sql'            : 'select count(*) from test_table having sleep(1)',
                    'num_calls'      : 1,
                    'total_ms'       : 0,
                    'min_ms'         : 0,
                    'max_ms'         : 0,
                },
                total_ms=self.assertGreater,
                min_ms=self.assertGreater,
                max_ms=self.assertGreater)
        finally:
            self.test_env.tomcat.shutdown()


if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
