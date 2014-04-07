import newrelic.agenttest.app.java.server
import os
import time
from distutils.version import LooseVersion
import logging
import pprint
import subprocess
import zipfile
import stat
import shutil
import atexit

class Play2(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'play2'

    def __init__(self, config, test_env, **kwargs):
        super(Play2, self).__init__(config, test_env, **kwargs)
    
    
    def pre_startup(self):
        self._destination = os.path.join(self._config['path'], 'dist-out', self._config['default_app_lang'])
        if(LooseVersion(self.version) >= LooseVersion('2.2')):
            self._startFile = os.path.join(self._destination, self._config['default_app_name'] + '-1.0', 'bin', self._config['default_app_name'])
        else:
            self._startFile = os.path.join(self._destination, self._config['default_app_name'] + '-1.0', 'start')

        if 'orig-bindir' not in self._config:
            self._config['orig-bindir'] = self._config['bindir']
        self._config['bindir'] = os.path.join('dist-out', self._config['default_app_lang'], self._config['default_app_name'] + '-1.0', self._config['orig-bindir'])

        if(os.path.isfile(self._startFile)):
            atexit.register(lambda dest: not os.path.exists(dest) and shutil.rmtree(dest), os.path.join(self._config['path'], 'dist-out'))
            return
            
        logging.debug(
            pprint.pformat({
                'action' : 'build',
                'args'   : self._build_args(),
                'cwd '   : self._build_cwd(),
                'config' : self._config,
                'env'    : self._build_env()}))

        childfhs = { 'stdout' : subprocess.PIPE, 'stderr' : subprocess.PIPE}
        self._proc = subprocess.Popen(
            self._build_args(),
            cwd=self._build_cwd(),
            env=self._build_env(),
            **childfhs)
        
        proc_out = self._proc.communicate()  # Wait for it to finish execution
        if(self._proc.returncode != 0):
            print("BUILD ERROR:")
            print(proc_out[0].decode("utf-8"))
            print(proc_out[1].decode("utf-8"))
        
        self._unzipDist()

    def _build_args(self):
        return ['play', 'dist']

    def _build_cwd(self):
        return os.path.join(self._config['path'], self._config['default_app'])

    def _build_env(self):
        return {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'PATH'      : '{}:{}'.format(self._config['path'], os.environ['PATH'])
        }

    def _unzipDist(self):
        if(LooseVersion(self.version) >= LooseVersion('2.2')):
            zipPath = os.path.join('target', 'universal', self._config['default_app_name'] + '-1.0.zip')
        else:
            zipPath = os.path.join('dist', self._config['default_app_name'] + '-1.0.zip')
        distZip = zipfile.ZipFile(os.path.join(self._build_cwd(), zipPath))
        
        if not os.path.exists(self._destination):
            os.makedirs(self._destination)
        atexit.register(lambda dest: not os.path.exists(dest) and shutil.rmtree(dest), os.path.join(self._config['path'], 'dist-out'))
        
        distZip.extractall(self._destination)
        
        st = os.stat(self._startFile)
        os.chmod(self._startFile, st.st_mode | stat.S_IEXEC)

    def _startup_args(self):
        args = list(self._config['startup_args'])
        jvm_args = self.get_jvm_args()
        if(LooseVersion(self.version) >= LooseVersion('2.2')):
            jvm_args[:] = [arg if arg.startswith('-D') else '-J' + arg for arg in jvm_args]
        args.extend(jvm_args)
        return args

    def shutdown(self):
        if not self._running:
            return
        if self._proc:
            self._proc.terminate()
            self._proc.wait()
            self._running = False
            self._proc = None

    def _env(self):
        return {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'PATH'      : '{}:{}'.format(os.environ['PATH'],
                                         os.path.join(self._config['path'], self._config['bindir']))
        }


class Play2App(newrelic.agenttest.app.java.server.HTTPServer):
    config_name = 'play2_app'

    def __init__(self, config, test_env, **kwargs):
        super(Play2App, self).__init__(config, test_env, **kwargs)

    def _startup_args(self):
        args = list(self._config['startup_args'])
        jvm_args = self.get_jvm_args()
        if(LooseVersion(self.version) >= LooseVersion('2.2')):
            jvm_args[:] = [arg if arg.startswith('-D') else '-J' + arg for arg in jvm_args]
        args.extend(jvm_args)
        return args

    def shutdown(self):
        if not self._running:
            return
        if self._proc:
            self._proc.terminate()
            self._proc.wait()
            self._running = False
            self._proc = None

    def _env(self):
        return {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'PATH'      : '{}:{}'.format(os.environ['PATH'],
                                         os.path.join(self._config['path'], self._config['bindir']))
        }

