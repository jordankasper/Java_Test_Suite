from newrelic.agenttest.apptools import app_decorator

import newrelic.agenttest.app.java.glassfish
import newrelic.agenttest.app.java.jre
import newrelic.agenttest.app.java.agent
import newrelic.agenttest.app.java.jboss
import newrelic.agenttest.app.java.jetty
import newrelic.agenttest.app.java.jms
import newrelic.agenttest.app.java.play
import newrelic.agenttest.app.java.play2
import newrelic.agenttest.app.java.resin
import newrelic.agenttest.app.java.tomcat
import newrelic.agenttest.app.java.tomee
import newrelic.agenttest.app.java.webapp
import newrelic.agenttest.app.java.wildfly
import newrelic.agenttest.app.java.metricservlet

__all__ = [
    'glassfish',
    'grails1_app',
    'grails2_app',
    'java',
    'java_agent',
    'java_test_webapp',
    'spring_mvc_showcase',
    'spring_petclinic',
    'spring_mvc_31_demo',
    'quartz_test',
    'jboss',
    'wildfly',
    'jetty',
    'play',
    'play2',
    'play2app',
    'resin',
    'tomcat',
    'tomee',
    'metric_servlet',
    'activemq',
    'hornetq'
]

glassfish             = app_decorator(newrelic.agenttest.app.java.glassfish.Glassfish)
grails1_app           = app_decorator(newrelic.agenttest.app.java.webapp.Grails1Webapp)
grails2_app           = app_decorator(newrelic.agenttest.app.java.webapp.Grails2Webapp)
java                  = app_decorator(newrelic.agenttest.app.java.jre.Java)
java_agent            = app_decorator(newrelic.agenttest.app.java.agent.Agent)
java_test_webapp      = app_decorator(newrelic.agenttest.app.java.webapp.TestWebapp)
spring_mvc_showcase   = app_decorator(newrelic.agenttest.app.java.webapp.Spring32Webapp)
spring_petclinic      = app_decorator(newrelic.agenttest.app.java.webapp.Spring30Webapp)
spring_mvc_31_demo    = app_decorator(newrelic.agenttest.app.java.webapp.Spring31Webapp)
quartz_test           = app_decorator(newrelic.agenttest.app.java.webapp.QuartzWebapp)
jboss                 = app_decorator(newrelic.agenttest.app.java.jboss.JBoss)
wildfly               = app_decorator(newrelic.agenttest.app.java.wildfly.WildFly)
jetty                 = app_decorator(newrelic.agenttest.app.java.jetty.Jetty)
play                  = app_decorator(newrelic.agenttest.app.java.play.Play)
play2                 = app_decorator(newrelic.agenttest.app.java.play2.Play2)
play2app              = app_decorator(newrelic.agenttest.app.java.play2.Play2App)
resin                 = app_decorator(newrelic.agenttest.app.java.resin.Resin)
tomcat                = app_decorator(newrelic.agenttest.app.java.tomcat.Tomcat)
tomee                 = app_decorator(newrelic.agenttest.app.java.tomee.TomEE)
metric_servlet        = app_decorator(newrelic.agenttest.app.java.metricservlet.Servlet)
activemq              = app_decorator(newrelic.agenttest.app.java.jms.ActiveMQ)
hornetq               = app_decorator(newrelic.agenttest.app.java.jms.HornetQ)
