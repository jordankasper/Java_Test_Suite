#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class Grails1Test(TestCase):

    @collector
    @java_agent
    @java
    @grails1_app
    @tomcat(select={'version' : 7})
    def test_grails_1_3_4(self):
        self.assertTrue(
                        self.test_env.tomcat.get_path('/petclinic-0.1/clinic/vets'))
        self.assertTrue(
                        self.test_env.tomcat.get_path_and_shutdown('/petclinic-0.1/owner/find'))        

        self.assertInstrumentation({'grails-1.3': True, 'servlet-2.4': True, 'hibernate-3.3': True })
        
        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/GrailsController/clinic/vets'),
                                  { 'count' : 1 })

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/GrailsController/owner/find'),
                                  { 'count' : 1 })       

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('Java/org.codehaus.groovy.grails.web.servlet.mvc.SimpleGrailsControllerHelper/handleURI'),
                                  { 'count' : 2 })
                # I have seen Custom/org.codehaus.groovy.grails.web.servlet.mvc.SimpleGrailsControllerHelper/handleURI oscillate between 1 and 2


if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
