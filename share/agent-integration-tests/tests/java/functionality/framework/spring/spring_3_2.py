#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class SpringTest(TestCase):

    @collector
    @java_agent
    @java
    @spring_mvc_showcase
    @tomcat(select={'version' : 7})
    def test_spring_home(self):
        self.assertTrue(
                        self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-showcase/'))
        
        self.assertInstrumentation({'spring-aop-2': True, 'servlet-2.4': True})
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('Java/org.springframework.web.servlet.DispatcherServlet/doDispatch'),
                                  { 'count' : 1 })
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('Jsp/WEB-INF/views/home.jsp'),
                                  { 'count' : 1 })

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('SpringView/home'),
                                  { 'count' : 1 })

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/JSP/WEB-INF/views/home.jsp'),
                                  { 'count' : 1 })

    
    @collector
    @java_agent
    @java
    @spring_mvc_showcase
    @tomcat(select={'version' : 7})
    def test_spring_form(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-showcase/form'))
        
        self.assertInstrumentation({'spring-aop-2': True, 'servlet-2.4': True})
        
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/FormController/form'),
            {'count' : 1},count=self.assertGreaterEqual)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Jsp/WEB-INF/views/form.jsp'),
            {'count' : 1},count=self.assertGreaterEqual)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Spring/Java/org.springframework.samples.mvc.form.FormController/form'),
            {'count' : 1},count=self.assertGreaterEqual)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('HttpDispatcher'),
            {'count' : 1},count=self.assertGreaterEqual)


    @collector
    @java_agent
    @java
    @spring_mvc_showcase
    @tomcat(select={'version' : 7})
    def test_spring_data(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-showcase/data/path/foo'))
        
        self.assertInstrumentation({'spring-aop-2': True, 'servlet-2.4': True})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/RequestDataController/withPathVariable'),
            {'count' : 1},count=self.assertGreaterEqual)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Spring/Java/org.springframework.samples.mvc.data.RequestDataController/withPathVariable'),
            {'count' : 1},count=self.assertGreaterEqual)


    @collector
    @java_agent
    @java
    @spring_mvc_showcase
    @tomcat(select={'version' : 7})
    def test_spring_writer(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-showcase/data/standard/response/writer'))
        
        self.assertInstrumentation({'spring-aop-2': True, 'servlet-2.4': True})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/StandardArgumentsController/availableStandardResponseArguments'),
            {'count' : 1},count=self.assertGreaterEqual)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Spring/Java/org.springframework.samples.mvc.data.standard.StandardArgumentsController/availableStandardResponseArguments'),
            {'count' : 1},count=self.assertGreaterEqual)


    @collector
    @java_agent
    @java   
    @spring_mvc_showcase
    @tomcat(select={'version' : 7})
    def test_spring_response(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-showcase/response/charset/accept'))
        
        self.assertInstrumentation({'spring-aop-2': True, 'servlet-2.4': True})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/ResponseController/responseAcceptHeaderCharset'),
            {'count' : 1},count=self.assertGreaterEqual)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Spring/Java/org.springframework.samples.mvc.response.ResponseController/responseAcceptHeaderCharset'),
            {'count' : 1},count=self.assertGreaterEqual)


    @collector
    @java_agent
    @java
    @spring_mvc_showcase
    @tomcat(select={'version' : 7})
    def test_spring_views(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/spring-mvc-showcase/views/pathVariables/bar/apple'))
        
        self.assertInstrumentation({'spring-aop-2': True, 'servlet-2.4': True})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/ViewsController/pathVars'),
            {'count' : 1},count=self.assertGreaterEqual)

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('Spring/Java/org.springframework.samples.mvc.views.ViewsController/pathVars'),
            {'count' : 1},count=self.assertGreaterEqual)

if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
