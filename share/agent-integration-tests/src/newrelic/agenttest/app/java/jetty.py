#from newrelic.agenttest.app.java.server import HTTPServer
import newrelic.agenttest.app.java.server
from datetime import datetime, date
import os
import time

class Jetty(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'jetty'

    def _env(self):
        env = self._no_agent_env()

        if self._test_env.get_var('javaagent'):
            jvm_args = self.get_jvm_args()
            env['JAVA_OPTIONS'] = ' '.join(jvm_args)

        return env

    def _no_agent_env(self):
        env = {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'JAVA' : os.path.join(self._test_env.get_var('java_bin'), 'java'),
            'PATH' : os.environ['PATH'] + ':'
                + os.path.join(self._config['path'], self._config['bindir'])
        }
        return env

    def is_valid_config(self):
        if self.version >= 9:
            return self._test_env.java.version >= 7

        elif self.version >= 8:
            return self._test_env.java.version >= 6

        return True

    def pre_startup(self):
        self.delete_log_file()

    def wait_for_startup(self, timeout=120):
        self.wait_for_startup_message(timeout)

    def log_file_path(self):
        today = date.fromtimestamp(time.time()).isoformat()
        prefix = datetime.strptime(today, "%Y-%m-%d").strftime("%Y_%m_%d")
        log_file = '{}.{}'.format(prefix, self._config['log_file'])
        return '{}/{}/{}'.format(self._config['path'],
                self._config['log_path'],
                log_file)
