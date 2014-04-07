import copy
import logging
import newrelic.agenttest.app.java.server
import os
import pprint
import re
import shutil
import subprocess
import time
import xml.dom.minidom

class Glassfish(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'glassfish'

    def __init__(self, config, test_env, **kwargs):
        super(Glassfish, self).__init__(config, test_env, **kwargs)
        self._warfiles = []
        self._test_env.set_var('custom_warfile_deploy', self.deploy_war)

    def deploy_war(self, warfile):
        self._warfiles.append(warfile)

    def _env(self):
        return {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'JAVA' : os.path.join(self._test_env.get_var('java_bin'), 'java'),
            'PATH'      : '{}:{}'.format(os.environ['PATH'],
                                         os.path.join(self._config['path'], self._config['bindir']))
        }

    def startup(self):
        self._write_java_to_config()
        if (self._test_env.get_var('javaagent') or self._warfiles) and not self._running:
            self._write_agent_to_config(self._test_env.get_var('javaagent'))
            super(Glassfish, self).startup()
            self._deploy_wars()
            self.wait_for_deploy(timeout=60)
        else:
            super(Glassfish, self).startup()

    def is_valid_config(self):
        if self.version >= 4:
            return self._test_env.java.version >= 7
        else:
            return True

    def wait_for_startup(self, timeout=60):
        self.list_domains(timeout)

    def list_domains(self, timeout=60):
        for _ in range(timeout):
            time.sleep(1)
            p = subprocess.Popen(
                self._list_domains_args(),
                cwd = self._cwd(),
                env = self._env(),
                stdout=subprocess.PIPE)
            result_bytes = p.communicate()[0]
            result_string = result_bytes.decode("utf-8")
            if result_string.startswith("domain1 running"):
                logging.debug('server started')
                break
        else:
            raise Exception('timed out waiting for server startup')

    def _list_domains_args(self):
        return self._config['list_domains_args']

    def wait_for_deploy(self, timeout=60):
        self.list_applications(timeout)

    def list_applications(self, timeout=60):
        if (len(self._warfiles) == 0):
            return
        appPath = self._warfiles[0]
        appName = self.getAppName(appPath)
        for _ in range(timeout):
            time.sleep(1)
            p = subprocess.Popen(
                self._list_applications_args(),
                cwd = self._cwd(),
                env = self._env(),
                stdout=subprocess.PIPE)
            result_bytes = p.communicate()[0]
            result_string = result_bytes.decode("utf-8")
            if (result_string.find(appName) != -1):
                logging.debug('server deployed {}'.format(appName))
                break
        else:
            raise Exception('timed out waiting for server to deploy')

    def _list_applications_args(self):
        return self._config['list_applications_args']
    
    def getAppName(self, appPath):
        regex_string = '.*/([^/]+).war'
        regex = re.compile(regex_string)
        match = regex.search(appPath);
        if match:
            return match.group(1)

    def _deploy_wars(self):
        args = self._config['deploy_args']
        childfhs = self._get_child_fhs()
        for war in self._warfiles:
            warargs = copy.deepcopy(args)
            warargs.append(war)
            logging.debug('deploying: ' + pprint.pformat(warargs))
            subprocess.Popen(
                warargs,
                env = self._env(),
                **childfhs)

        for fh in childfhs.values():
            fh.close()

    def _undeploy_wars(self):
        args = self._config['undeploy_args']
        childfhs = self._get_child_fhs()
        for war in self._warfiles:
            m = re.match('.*/([^/]+).war', war)
            deploy_name = m.group(1)
            warargs = copy.deepcopy(args)
            warargs.append(deploy_name)
            logging.debug('undeploying: ' + pprint.pformat(warargs))
            subprocess.Popen(
                warargs,
                env = self._env(),
                **childfhs)

        for fh in childfhs.values():
            fh.close()

    def _write_java_to_config(self): 
        config_path = self._config['java_conf_path']
        logging.debug(config_path)
        self._reset_config(config_path)
        line_to_write = 'AS_JAVA="' + self._test_env.get_var('java_home') + '"'
        logging.debug(line_to_write)
        open_file = open(config_path, "a")
        line = open_file.write(line_to_write )
        open_file.close()
        

    def _write_agent_to_config(self, agent_path):
        self._reset_config(self._config['config_path'])
        conf_path = self._config['config_path']
        conf_xml = xml.dom.minidom.parse(conf_path)
        nodes = conf_xml.getElementsByTagName('java-config')

        for node in nodes:
            jvm_args = self.get_jvm_args()
            for jvm_arg in jvm_args:
                elem = conf_xml.createElement('jvm-options')
                elem.appendChild(conf_xml.createTextNode(jvm_arg))
                node.appendChild(elem)

            '''
            elem = conf_xml.createElement('jvm-options')
            elem.appendChild(conf_xml.createTextNode(
                    '-Xbootclasspath/a:{}'.format(agent_path)))
            node.appendChild(elem)
            '''

            '''
            elem = conf_xml.createElement('jvm-options')
            elem.appendChild(conf_xml.createTextNode(
                    '-Dnewrelic.config.log_level=finest'))
            node.appendChild(elem)
            '''

            '''
            elem = conf_xml.createElement('jvm-options')
            elem.appendChild(conf_xml.createTextNode(
                    '-Xdebug-'))
            node.appendChild(elem)

            elem = conf_xml.createElement('jvm-options')
            elem.appendChild(conf_xml.createTextNode(
                    '-Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=7001'))
            node.appendChild(elem)

            elem = conf_xml.createElement('jvm-options')
            elem.appendChild(conf_xml.createTextNode(
                    '-Xnoagent'))
            node.appendChild(elem)
            '''
        with open(conf_path, 'w+') as f:
            f.write(conf_xml.toprettyxml(encoding='UTF-8').decode())

    def _reset_config(self, conf_path):
        back_up = conf_path + '.new'
        if os.path.isfile(back_up):
          shutil.copy(back_up, conf_path)
        else:
          shutil.copy(conf_path, back_up)

    def shutdown(self):
        if self._running:
            logging.debug('undeploying wars')
            self._undeploy_wars()
            logging.debug('reverting config')
            self._write_java_to_config()
            self._reset_config(self._config['config_path'])

        super(Glassfish, self).shutdown()
