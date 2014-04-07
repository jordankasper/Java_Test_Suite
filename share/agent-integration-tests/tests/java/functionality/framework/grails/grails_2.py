#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import *
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class Grails2Test(TestCase):

    @collector
    @java_agent
    @java(select={'version' : 7})
    @grails2_app
    @tomcat(select={'version' : 7})
    def test_grails_2_tomcat(self):
        self.assertTrue(
                        self.test_env.tomcat.get_path('/petclinic-0.1/clinic/vets'))
        self.assertTrue(
                        self.test_env.tomcat.get_path_and_shutdown('/petclinic-0.1/owner/find'))

        self.assertInstrumentation({'grails-2': True, 'hibernate-3.5': True, 'servlet-2.4': True, 'spring-aop-2': True })


        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/GrailsController/clinic/vets'),
                                  { 'count' : 1 })

        self.assertIterAttributes(
                                  self.test_env.collector.get_unscoped_metrics('WebTransaction/GrailsController/owner/find'),
                                  { 'count' : 1 })


if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
