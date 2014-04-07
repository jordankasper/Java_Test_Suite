import copy
import newrelic.agenttest.app.java.server
import os
import shutil
import xml.dom.minidom

class Resin(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'resin'

    def _env(self):
        env = {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'JAVA' : os.path.join(self._test_env.get_var('java_bin'), 'java'),
            'PATH' : os.environ['PATH'] + ':'
                + os.path.join(self._config['path'], self._config['bindir'])
        }

        return env

    def is_valid_config(self):
        if self.version == 4:
            return self._test_env.java.version >= 6
        else:
            return True

    def pre_startup(self):
        self.delete_log_file()

    def wait_for_startup(self, timeout=60):
        self.wait_for_startup_message(timeout)

    def startup(self):
        if self._test_env.get_var('javaagent') and not self._running:
            shutil.copytree(
                os.path.join(self._config['path'], 'conf'),
                os.path.join(self._test_env.get_var('working_dir'), 'conf'))

            self._conf_path = os.path.join(
                self._test_env.get_var('working_dir'),
                'conf',
                self._config['config_file'])

            self._apply_agent_settings(
                self._test_env.get_var('javaagent'))

        super(Resin, self).startup()

    def shutdown(self):
        if self._running:
            # cleanup the working directory or else
            # resin won't autodeploy the warfile next run
            shutil.rmtree(
                os.path.join(
                    self._test_env.get_var('working_dir'),
                    'java_test_webapp',
                    'META-INF'))

            shutil.rmtree(
                os.path.join(
                    self._test_env.get_var('working_dir'),
                    'java_test_webapp',
                    'WEB-INF'))

            shutil.rmtree(os.path.dirname(self._conf_path))

        super(Resin, self).shutdown()

    def _startup_args(self):
        args = copy.deepcopy(self._config['startup_args'])
        args.extend(['-conf', self._conf_path])
        return args

    def _apply_agent_settings(self, agent_path):
        conf_xml = xml.dom.minidom.parse(self._conf_path)
        jvm_arg_parent_node = conf_xml.getElementsByTagName(
            self._config['jvm_arg_parent_node'])
        jvm_args = self.get_jvm_args()
        for jvm_arg in jvm_args:
            elem = conf_xml.createElement('jvm-arg')
            elem.appendChild(conf_xml.createTextNode(jvm_arg))
            jvm_arg_parent_node[0].appendChild(elem)

#        elem = conf_xml.createElement('jvm-arg')
#        elem.appendChild(conf_xml.createTextNode(
#                '-Dnewrelic.config.log_level=finest'))
#        jvm_arg_parent_node[0].appendChild(elem)

        with open(self._conf_path, 'w+') as f:
            f.write(conf_xml.toprettyxml(encoding='UTF-8').decode())
