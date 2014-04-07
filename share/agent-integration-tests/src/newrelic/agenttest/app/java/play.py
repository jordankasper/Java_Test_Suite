import newrelic.agenttest.app.java.server
import os.path
import logging

class Play(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'play'

    def __init__(self, config, test_env, **kwargs):
        super(Play, self).__init__(config, test_env, **kwargs)
        custom = kwargs.get('custom', {})
        self._app = os.path.join(
            config['path'], custom.get('app', self._config['default_app']))
        self._remove_old_pid();

    def _startup_args(self):
        args = list(self._config['startup_args'])
        args.append(self._app)
        return args

    def _remove_old_pid(self):
        file_paths = self._config['pid_file'].split(',')
        for path in file_paths:
            logging.debug('deleting path if present: ' + path)     
            if os.path.isfile(path):
                os.remove(path)

    def _shutdown_args(self):
        args = list(self._config['shutdown_args'])
        args.append(self._app)
        return args

    def _env(self):
        env = self._no_agent_env()

        if self._test_env.get_var('javaagent'):
            jvm_args = self.get_jvm_args()
            env['JAVA_OPTS'] = ' '.join(jvm_args)

        return env

    def _no_agent_env(self):
        return {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'PATH'      : self._config['path'] + ':' + os.environ['PATH']
        }

    def is_valid_config(self):
        return self._test_env.java.version >= 7
