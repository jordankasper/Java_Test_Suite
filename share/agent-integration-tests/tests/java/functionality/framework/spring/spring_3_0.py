#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class SpringTest(TestCase):

    @collector
    @java_agent
    @java
    @spring_petclinic
    @tomcat(select={'version' : 7})
    def test_spring_welcome(self):
        self.assertTrue(
                        self.test_env.tomcat.get_path_and_shutdown('/petclinic/'))
        
        self.assertInstrumentation({'servlet-2.4': True})
        
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/ClinicController/welcomeHandler'),
                                  { 'count' : 1 })

    
    @collector
    @java_agent
    @java
    @spring_petclinic
    @tomcat(select={'version' : 7})
    def test_spring_vets(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/petclinic/vets'))
        
        self.assertInstrumentation({'spring-aop-2': True, 'servlet-2.4': True})
        
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/ClinicController/vetsHandler'),
            {'count' : 1})


    @collector
    @java_agent
    @java
    @spring_petclinic
    @tomcat(select={'version' : 7})
    def test_spring_search(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/petclinic/owners/search'))
        
        self.assertInstrumentation({'servlet-2.4': True})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/FindOwnersForm/setupForm'),
            {'count' : 1})


    @collector
    @java_agent
    @java
    @spring_petclinic
    @tomcat(select={'version' : 7})
    def test_spring_owners(self):
        self.assertTrue(
            self.test_env.tomcat.get_path_and_shutdown('/petclinic/owners?lastName='))
        
        self.assertInstrumentation({'spring-aop-2': True, 'servlet-2.4': True})

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/SpringController/FindOwnersForm/processSubmit'),
            {'count' : 1})


if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
