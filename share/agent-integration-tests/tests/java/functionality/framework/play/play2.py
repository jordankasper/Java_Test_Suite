#!/usr/bin/env python3

from newrelic.agenttest.app.testdecorators import collector
from newrelic.agenttest.app.java.testdecorators import *
from newrelic.agenttest.unittest import *
from newrelic.collector import CollectorHTTPServer

class Play2Test(TestCase):

    @collector
    @java_agent
    @java
    @play2app
    def test_scala(self):
        self.assertTrue(self.test_env.play2_app.get_path('/scala'))  # First call should be ignored
        self.assertTrue(self.test_env.play2_app.get_path('/scala'))
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayControllerAction/controllers.ScalaApplication.index'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        self.test_env.play2_app.shutdown()

    @collector
    @java_agent
    @java
    @play2app
    def test_newrelic_api_scala(self):
        self.assertTrue(self.test_env.play2_app.get_path('/hello-scala'))  # First call should be ignored
        self.assertTrue(self.test_env.play2_app.get_path('/hello-scala'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/CustomTest/HelloScalaTransaction'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        self.test_env.play2_app.shutdown()

    @collector
    @java_agent
    @java
    @play2app
    def test_newrelic_api_java(self):
        self.assertTrue(self.test_env.play2_app.get_path('/hello-java'))  # First call should be ignored
        self.assertTrue(self.test_env.play2_app.get_path('/hello-java'))
        
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/CustomTest/HelloJavaTransaction'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        self.test_env.play2_app.shutdown()

    @collector
    @java_agent
    @java
    @play2app
    def test_java(self):
        self.assertTrue(self.test_env.play2_app.get_path('/java'))  # First call should be ignored
        self.assertTrue(self.test_env.play2_app.get_path('/java'))

        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayControllerAction/controllers.JavaApplication.index'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        self.test_env.play2_app.shutdown()

    @collector
    @java_agent
    @java
    @play2app
    def test_scala_async(self):
        self.assertTrue(self.test_env.play2_app.get_path('/scala-async'))  # First call should be ignored
        self.assertTrue(self.test_env.play2_app.get_path('/scala-async'))
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayControllerAction/controllers.AsyncScalaApplication.index'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        self.test_env.play2_app.shutdown()

    @collector
    @java_agent
    @java
    @play2app
    def test_java_async(self):
        self.assertTrue(self.test_env.play2_app.get_path('/java-async'))  # First call should be ignored
        self.assertTrue(self.test_env.play2_app.get_path('/java-async'))
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayControllerAction/controllers.AsyncJavaApplication.index'),
            {
                'count'      : 1,
                'total_time' : 0
            },
            total_time=self.assertGreater)

        self.test_env.play2_app.shutdown()

    @collector
    @java_agent
    @java
    @play2app
    #@play2app(select={'version' : [2.1, 2.2]})
    #@play2app(select={'version' : [2.1.5, 2.2.0]})
    def test_scala_timeout(self):
        self.assertTrue(self.test_env.play2_app.get_path('/scala-timeout'))  # First call should be ignored
        self.assertTrue(self.test_env.play2_app.get_path('/scala-timeout'))
 
        self.assertIterAttributes(
            self.test_env.collector.get_unscoped_metrics('WebTransaction/PlayControllerAction/controllers.ScalaApplication.timeout'),
            {
                'count'      : 1,
                'total_time' : 30
            },
            total_time=self.assertLess)

        self.test_env.play2_app.shutdown()


if __name__ == '__main__':
    newrelic.agenttest.unittest.initenv(__file__)
    newrelic.agenttest.unittest.main()
