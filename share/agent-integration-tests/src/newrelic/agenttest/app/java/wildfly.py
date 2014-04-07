import newrelic.agenttest.app.java.server
import os

class WildFly(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'wildfly'

    def _init_webapp_env(self):
        self._test_env.set_var(
            'webapp_path',
            os.path.join(self._config['path'], self._config['deploy_path']))
        self._test_env.set_var('expand_warfile', False)

    def is_valid_config(self):
        return self._test_env.java.version >= 7

    def pre_startup(self):
        self.delete_log_file()

    def wait_for_startup(self, timeout=120):
        self.wait_for_startup_message(timeout)

    def wait_for_shutdown(self, timeout=60):
        self.wait_for_shutdown_message(timeout)
