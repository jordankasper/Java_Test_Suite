#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class SpringTest(TestCase):

    @collector
    @java_agent
    @java
    @spring_mvc_31_demo
    @tomcat(select={'version' : 7})
    def test_spring_home(self):
        self.assertTrue(
                        self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-31-demo/'))
        
        self.assertInstrumentation({'servlet-2.4': True})
        
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/JSP/WEB-INF/views/home.jsp'),
                                  { 'count' : 1 })

    
    @collector
    @java_agent
    @java
    @spring_mvc_31_demo
    @tomcat(select={'version' : 7})
    def test_spring_accounts(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-31-demo/accounts'))
        
        self.assertInstrumentation({'servlet-2.4': True})
        
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/AccountController/list'),
            {'count' : 1})


    @collector
    @java_agent
    @java
    @spring_mvc_31_demo
    @tomcat(select={'version' : 7})
    def test_spring_new(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-31-demo/accounts/new'))
        
        self.assertInstrumentation({'servlet-2.4': True})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/AccountController/newForm'),
            {'count' : 1})



if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
