import newrelic.agenttest.app
import newrelic.collector
import time

class Collector(newrelic.agenttest.app.BaseApp):
    config_name = 'collector'

    def __init__(self, config, test_env, **kwargs):
        super(__class__, self).__init__(config, test_env)
        self._collector_options = kwargs.get('custom', {})
        test_env.set_var('collector_port', config['port'])
        test_env.set_var('collector_host', config['host'])

    def startup(self):
        self._collector = newrelic.collector.CollectorHTTPServer(
            tuple([self._config['host'], self._config['port']]), **self._collector_options)
        self._collector.startup()

    def shutdown(self):
        self._collector.shutdown()

    def _sorted_copy(self, vals, sort_attr):
        vals_copy = vals
        vals_copy.sort(key = lambda v: getattr(v, sort_attr))
        return vals_copy

    def get_transaction_traces(self, name):
        self._wait_for_transaction_traces(name=name)
        return list(
            filter(
                lambda tt: tt.name == name,
                self._sorted_copy(self._collector.transaction_traces, 'name')))

    def get_sql_traces(self, name):
        self._wait_for_sql_traces(name=name)
        return list(
            filter(
                lambda m: m.name == name,
                self._sorted_copy(self._collector.sql_traces, 'name')))

    def get_unscoped_metrics(self, name=None, timeout=120):
        if name is None:
            return self._get_all_unscoped_metrics()
        else:
            self._wait_for_metrics(name=name, timeout=timeout)
            return list(
                filter(
                    lambda m: m.name == name and m.scope is None,
                    self._sorted_copy(self._collector.metrics, 'name')))

    def get_scoped_metrics(self, scope=None):
        if scope is None: 
            return self._get_all_scoped_metrics()
        else:
            self._wait_for_metrics(scope=scope)
            return list(
                filter(
                   lambda m: m.scope == scope,
                   self._sorted_copy(self._collector.metrics, 'name')))

    def get_profiles(self):
        self._wait_for_collector(
            lambda: getattr(self._collector, 'profiles'), 120)
        return self._collector.profiles

    def _get_all_unscoped_metrics(self):
        self._wait_for_collector(
            lambda: filter(
                lambda m: m.scope is None,
                self._collector.metrics),
            120)
        return list(
            filter(
                lambda m: m.scope is None,
                self._sorted_copy(self._collector.metrics, 'name')))

    def _get_all_scoped_metrics(self):
        self._wait_for_collector(
            lambda: filter(
                lambda m: m.scope is not None,
                self._collector.metrics),
            120)
        return list(
            filter(
                lambda m: m.scope is not None,
                self._sorted_copy(self._collector.metrics, 'name')))

    def get_errors(self):
        self._wait_for_collector(
            lambda: getattr(self._collector, 'errors'), 120)
        return self._collector.errors

    def get_events(self):
        self._wait_for_collector(
            lambda: getattr(self._collector, 'events'), 120)
        return self._collector.events
    
    def get_modules(self, name=None):
        if name is None:
            self._wait_for_collector(
                lambda: getattr(self._collector, 'modules'), 120)
            return self._collector.modules
        else:
            self._wait_for_modules(name=name)
            return list(
                filter(
                    lambda m: m.name == name,
                        self._sorted_copy(self._collector.modules, 'name')))
            
    def get_module_name(self):
        self._wait_for_collector(
            lambda: getattr(self._collector, 'mod_name'), 120)
        return self._collector.mod_name

    def get_messages(self):
        self._wait_for_collector(
            lambda: getattr(self._collector, 'messages'), 120)
        return self._collector.messages

    def _wait_for_metrics(self, name='', scope='', timeout=120):
        self._wait_for_collector(
            lambda: filter(
                lambda m: m.name == (name or m.name)
                    and m.scope == (scope or m.scope),
                self._collector.metrics),
            timeout)

    def _wait_for_transaction_traces(self, name='', timeout=120):
        self._wait_for_collector(
            lambda: filter(
                lambda tt: tt.name == (name or tt.name),
                self._collector.transaction_traces),
            timeout)

    def _wait_for_sql_traces(self, name='', timeout=120):
        self._wait_for_collector(
            lambda: filter(
                lambda st: st.name == (name or st.name),
                self._collector.sql_traces),
            timeout)
        
    def _wait_for_modules(self, name='', timeout=120):
        self._wait_for_collector(
            lambda: filter(
                lambda st: st.name == (name or st.name),
                self._collector.modules),
            timeout)

    def _wait_for_errors(self, timeout=120):
        self._wait_for_collector(
            lambda: self._collector.errors,
            timeout)

    def _wait_for_collector(self, func, timeout):
        for _ in range(timeout):
            if list(func()):
                break
            else:
                time.sleep(1)
        else:
            raise Exception('timeout waiting for collector')
