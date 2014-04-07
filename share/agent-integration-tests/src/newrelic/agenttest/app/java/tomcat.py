import newrelic.agenttest.app.java.server
import logging
import shutil
import os

class Tomcat(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'tomcat'

    def is_valid_config(self):
        if self.version >= 7:
            return self._test_env.java.version >= 6
        else:
            return True

    def _no_agent_env(self):
        return {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'PATH'      : '{}:{}'.format(os.environ['PATH'],
                                         os.path.join(self._config['path'], self._config['bindir'])),
            'CATALINA_PID' : self.pid_file_path()
        }

    def delete_log_file(self):
        log_file_path = self.log_file_path()
        try:
            shutil.copy(log_file_path, self._test_env.get_var('working_dir'))
            os.remove(log_file_path)
            logging.debug('deleted {}'.format(log_file_path))
        except OSError:
            pass
        except IOError:
            pass

    def pre_startup(self):
        self.delete_log_file()
        self.create_pid_file()

    def create_pid_file(self):
        '''
        Tomcat stores the pid in the file specified in the CATALINA_PID environment variable.
        The pid file is necessary to shutdown Tomcat using the -force option
        '''
        try:
            pid_file_path = self.pid_file_path()
            os.open(pid_file_path, os.O_CREAT)
            logging.debug('created pid file {}'.format(pid_file_path))
        except IOError:
            pass
        
    def pid_file_path(self):
        return os.path.join(self._test_env.get_var('working_dir'), 'catalina.pid')

    def wait_for_startup(self, timeout=120):
        self.wait_for_startup_message(timeout)
        
