from newrelic.agenttest.apptools import app_decorator

import newrelic.agenttest.app.collector

__all__ = ['collector']

collector = app_decorator(newrelic.agenttest.app.collector.Collector)
