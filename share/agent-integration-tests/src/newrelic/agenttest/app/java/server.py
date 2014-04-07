import logging
import newrelic.agenttest.app
import os
import pprint
import socket
import subprocess
import time
import shutil
import urllib.request
import re
from newrelic.agenttest import obfuscator

class HTTPServer(newrelic.agenttest.app.BaseApp):

    def __init__(self, config, test_env, **kwargs):
        super(HTTPServer, self).__init__(config, test_env, **kwargs)
        self._running = False
        self._proc = None
        self._html = None
        self._response_headers = []
        self._jvm_args = kwargs.get('jvm_args', [])
        self._init_webapp_env()

    def __enter__(self, *args):
        self.startup(*args)
        return self

    def __exit__(self, *args):
        self.shutdown(*args)

    def _init_webapp_env(self):
        self._test_env.set_var('webapp_path',
            os.path.join(self._config['path'], 'webapps'))
        self._test_env.set_var('expand_warfile', True)
        
    def get_port(self):
        return self._config['port']
        
    def clean_up_previous(self):
        delete_dir_path = self.delete_dir_path()
        if delete_dir_path is not None:
            try:
                if os.path.exists(delete_dir_path):
                    shutil.rmtree(delete_dir_path)
                    logging.debug('deleted {}'.format(delete_dir_path))
                else: 
                    logging.debug('{} already deleted'.format(delete_dir_path))   
            except OSError: 
                pass
            if os.path.exists(delete_dir_path):
                raise Exception('The server could not be cleaned up from a previous run. Could not delete ' + delete_dir_path)
            
    def delete_dir_path(self):
        if 'delete_dir' in self._config.keys():
            return '{}/{}'.format(self._config['path'],
                self._config['delete_dir'])
        else:
            return None

    def startup(self):
        if self._running:
            return

        if (self._is_server_active()):
            raise Exception('server already running, is there another process using this port?')
        
        self.clean_up_previous()
        
        self._running = True
        
        self.pre_startup()

        logging.debug(
            pprint.pformat({
                'action' : 'startup',
                'args'   : self._startup_args(),
                'cwd '   : self._cwd(),
                'config' : self._config,
                'env'    : self._env()}))
        
        start_time_millis = int(round(time.time() * 1000))

        childfhs = self._get_child_fhs()
        try:
            self._proc = subprocess.Popen(
                self._startup_args(),
                cwd = self._cwd(),
                env = self._env(),
                **childfhs)
        except FileNotFoundError:
            logging.warning(
                pprint.pformat({
                    'action' : 'startup',
                    'args'   : self._startup_args(),
                    'cwd '   : self._cwd(),
                    'config' : self._config,
                    'env'    : self._env()}))
            raise FileNotFoundError
        finally:
            for fh in childfhs.values():
                fh.close()        

        self.wait_for_startup()

        if (not self._is_server_active()):
            raise Exception('timed out waiting for server startup')
        
        end_time_millis = int(round(time.time() * 1000))
        logging.debug('server started in {} ms'.format(end_time_millis - start_time_millis))

    def pre_startup(self):
        pass

    def wait_for_startup(self, timeout=90):
        for i in range(timeout):
            if self._is_server_active():
                logging.debug('connected on attempt {}'.format(i + 1))
                break
            else:
                time.sleep(1)
        else:
            raise Exception('timed out waiting for server startup')

    def wait_for_startup_url(self, url, timeout=90):
        for i in range(timeout):
            try:
                request = urllib.request.Request(url)
                response = urllib.request.urlopen(request)
                if response:
                    logging.debug('connected to {} on attempt {}'.format(url, i + 1))
                    break
            except Exception:
                pass
            time.sleep(1)
        else:
            raise Exception('timed out waiting for server startup')

    def _cwd(self):
        return None

    def _env(self):
        env = self._no_agent_env()

        if self._test_env.get_var('javaagent'):
            jvm_args = self.get_jvm_args()
            env['JAVA_OPTS'] = ' '.join(jvm_args)

        return env

    def _no_agent_env(self):
        return {
            'JAVA_HOME' : self._test_env.get_var('java_home'),
            'PATH'      : '{}:{}'.format(os.environ['PATH'],
                                         os.path.join(self._config['path'], self._config['bindir']))
        }

    def get_jvm_args(self):
        jvm_args = []
        jvm_args.append('-javaagent:{}'.format(self._test_env.get_var('javaagent')))
        jvm_args.append('-Dnewrelic.config.host={}'.format(self._test_env.get_var('collector_host')))
        jvm_args.append('-Dnewrelic.config.port={}'.format(self._test_env.get_var('collector_port')))
        '''
        append the jvm_args in java_config.yml.  For example:
            jvm_args:      [ '-Dnewrelic.config.log_level=finest', '-Xmx1024m' ]
        '''
        jvm_args.extend(self._config.get('jvm_args', []))
        if self._jvm_args:
            '''
            append the jvm_args on the annotation. For example:
                @jetty(jvm_args=[ '-Dnewrelic.config.log_level=finest', '-Xmx1024m' ])
            '''
            jvm_args.extend(self._jvm_args)
        return jvm_args

    def _startup_args(self):
        return self._config['startup_args']

    def _get_child_fhs(self):
        if not logging.getLogger().isEnabledFor(logging.DEBUG):
            nullfh = open(os.devnull, 'w+')
            return {'stdin' : nullfh, 'stdout' : nullfh, 'stderr' : nullfh}
        else:
            return {}

    def _is_server_active(self):
        connected = False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self._config['host'], int(self._config['port'])))
            connected = True
        except socket.error:
            pass
        finally:
            if connected:
                s.shutdown(2)
            s.close()

        return connected

    def delete_log_file(self):
        log_file_path = self.log_file_path()
        try:
            os.remove(log_file_path)
            logging.debug('deleted {}'.format(log_file_path))
        except OSError:
            pass

    def log_file_path(self):
        return '{}/{}/{}'.format(self._config['path'],
                self._config['log_path'],
                self._config['log_file'])

    def wait_for_startup_message(self, timeout=90):
        log_file_path = self.log_file_path()
        msg = self._config['startup_msg']
        logging.debug('checking {} for startup message \'{}\''.format(log_file_path, msg))
        for _ in range(timeout // 2):
            time.sleep(2)
            if self._checkLogForMessage(log_file_path, msg):
                logging.debug('found startup message')
                return
        logging.debug('failed to find startup message after {} seconds'.format(timeout))

    def _checkLogForMessage(self, log_file_path, msg):
        found = False
        buffer = None
        try:
            buffer = open(log_file_path);
            if msg in buffer.read():
                found = True
        except IOError:
            pass
        finally:
            if buffer is not None:
                buffer.close()
        return found

    def get_path(self, path, data=None, headers={}, timeout=30, **kwargs):
        url = self.get_url(path, data, headers, **kwargs)

        for _ in range(10):
            try:
                return self.get_response(url, data, headers, timeout)
            except urllib.error.HTTPError as e:
                if e.code != 500:
                    time.sleep(1)
                else:
                    return
            except Exception as e:
                logging.warning(e)
                
    def get_url(self, path, data=None, headers={}, **kwargs):
        params = []
        for (k, v) in kwargs.items():
            params.append(k + '=' + urllib.request.quote(v))

        if params:
            path += '?' + '&'.join(params)

        url = 'http://{}:{}{}'.format(
                self._config['host'],
                int(self._config['port']),
                path)
        return url

    def get_response(self, url, data=None, headers={}, timeout=30):
        self._html = None
        self._response_headers = []
        request = urllib.request.Request(url, data=data, headers=headers)
        response = urllib.request.urlopen(request, timeout=timeout)
        self._html = response.read()
        self._response_headers = response.info().items()
        logging.debug(self._response_headers)
        return response

    def get_path_and_shutdown(self, path, data=None, headers={}, timeout=90, **kwargs):
        response = self.get_path(path, data, headers, timeout, **kwargs)
        self.shutdown()
        return response

    def get_response_header(self, name, regex=None, deobfuscate=False):
        if name is None:
            return None
        for header in self._response_headers:
            if header[0] == name:
                return self._get_response_header_value(name, header[1], regex, deobfuscate)
        return None

    def get_html(self):
        return self._html

    def _get_response_header_value(self, name, value, regex=None, deobfuscate=False):
        if deobfuscate :
            value = obfuscator.deobfuscate(value)
        if regex :
            match = re.compile(regex).search(value)
            if match :
                return match.group(0)
            else :
                raise Exception('regex failed to match {} response header: {}'.format(name, value))
        else :
            return value 

    def shutdown(self):
        if not self._running:
            return

        childfhs = self._get_child_fhs()
        logging.debug('shutting down server')

        start_time_millis = int(round(time.time() * 1000))

        try:
            p = subprocess.Popen(
                self._shutdown_args(),
                cwd = self._cwd(),
                env = self.shutdown_env(),
                **childfhs)
            p.wait()
            
            if (self._proc is not None):
                self._proc.wait()
                self._proc = None

        finally:
            for fh in childfhs.values():
                fh.close()
            self._running = False
            
        self.wait_for_shutdown()

        end_time_millis = int(round(time.time() * 1000))
        logging.debug('server shutdown in {} ms'.format(end_time_millis - start_time_millis))

    def wait_for_shutdown(self, timeout=60):
        pass

    def wait_for_shutdown_message(self, timeout=60):
        log_file_path = self.log_file_path()
        msg = self._config['shutdown_msg']
        logging.debug('checking {} for shutdown message \'{}\''.format(log_file_path, msg))
        for _ in range(timeout // 2):
            time.sleep(2)
            if self._checkLogForMessage(log_file_path, msg):
                logging.debug('found shutdown message')
                return
        logging.debug('failed to find shutdown message after {} seconds'.format(timeout))

    def _shutdown_args(self):
        return self._config['shutdown_args']
    
    def shutdown_env(self):
        return self._no_agent_env()
