import logging
import newrelic.agenttest.app.java.server
import os
import time

class JBoss(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'jboss'

    def _init_webapp_env(self):
        self._test_env.set_var(
            'webapp_path',
            os.path.join(self._config['path'], self._config['deploy_path']))
        self._test_env.set_var('expand_warfile', False)

    def is_valid_config(self):
        if self.version >= 7:
            return self._test_env.java.version >= 7
        elif self.version >= 6:
            return self._test_env.java.version >= 6 and self._test_env.java.version < 7
        else:
            return True

    def pre_startup(self):
        self.delete_log_file()
        self.delete_shutdown_log_file()

    def wait_for_startup(self, timeout=300):
        self.wait_for_startup_message(timeout)
        
    def wait_for_shutdown(self, timeout=60):
        self.wait_for_shutdown_message(timeout)

    def wait_for_shutdown_message(self, timeout=60):
        log_file_path = self.shutdown_log_file_path()
        msg = self._config['shutdown_msg']
        logging.debug('checking {} for shutdown message \'{}\''.format(log_file_path, msg))
        for _ in range(timeout // 2):
            time.sleep(2)
            if self._checkLogForMessage(log_file_path, msg):
                logging.debug('found shutdown message')
                return
        logging.debug('failed to find shutdown message after {} seconds'.format(timeout))

    def shutdown_log_file_path(self):
        return '{}/{}/{}'.format(self._config['path'],
                self._config['log_path'],
                self._config['shutdown_log_file'])

    def delete_shutdown_log_file(self):
        log_file_path = self.shutdown_log_file_path()
        try:
            os.remove(log_file_path)
            logging.debug('deleted {}'.format(log_file_path))
        except OSError:
            pass


