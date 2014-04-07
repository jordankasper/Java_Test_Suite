import newrelic.agenttest.app.java.server
import os
import logging
import time

class ActiveMQ(newrelic.agenttest.app.BaseApp):
    config_name = 'activemq'

    def startup(self):
        log_file_path = self.log_file_path()
        os.system(
            '/bin/rm -f {} > /dev/null'.format(
                log_file_path))
        app_path = self._config['path']
        self._running = False
        os.system(
            'cd {} && {}/bin/activemq start > /dev/null'.format(
                app_path,
                app_path))
        self.wait_for_startup()
        if (not self._running):
            raise Exception('timed out waiting for activemq startup')
        return self

    def shutdown(self):
        app_path = self._config['path']
        self._running = True
        os.system(
            'cd {} && {}/bin/activemq stop > /dev/null'.format(
                app_path,
                app_path))
        self.wait_for_shutdown()
        if (self._running):
            raise Exception('timed out waiting for activemq shutdown')
        return self

    def wait_for_startup(self, timeout=60):
        self.wait_for_startup_message(timeout)

    def wait_for_startup_message(self, timeout=60):
        log_file_path = self.log_file_path()
        startup_msg = self._config['startup_msg']
        logging.debug('checking {} for startup message \'{}\''.format(log_file_path, startup_msg))
        for _ in range(timeout // 2):
            time.sleep(2)
            if self._checkLogForMessage(log_file_path, startup_msg):
                self._running = True
                logging.debug('found startup message')
                return
        logging.debug('failed to find startup message after {} seconds'.format(timeout))


    def _checkLogForMessage(self, log_file_path, desired_msg):
        found = False
        buffer = None
        try:
            buffer = open(log_file_path);
            if desired_msg in buffer.read():
                found = True
        except IOError:
            pass
        finally:
            if buffer is not None:
                buffer.close()
        return found

    def wait_for_shutdown(self, timeout=60):
        self.wait_for_shutdown_message(timeout)

    def wait_for_shutdown_message(self, timeout=60):
        log_file_path = self.log_file_path()
        msg = self._config['shutdown_msg']
        logging.debug('checking {} for shutdown message \'{}\''.format(log_file_path, msg))
        for _ in range(timeout // 2):
            time.sleep(2)
            if self._checkLogForMessage(log_file_path, msg):
                self._running = False
                logging.debug('found shutdown message')
                return
        logging.debug('failed to find shutdown message after {} seconds'.format(timeout))


    def log_file_path(self):
        return '{}/{}/{}'.format(self._config['path'],
                self._config['log_path'],
                self._config['log_file'])


class HornetQ(newrelic.agenttest.app.BaseApp):
    config_name = 'hornetq'

    def startup(self):
        hornetq_template = self._config['config_path']
        app_path = self._config['path']
        logging.debug(
            '/bin/cp {} {}/config/stand-alone/non-clustered/hornetq-jms.xml'.format(
                hornetq_template,
                app_path))
        os.system(
            '/bin/cp {} {}/config/stand-alone/non-clustered/hornetq-jms.xml'.format(
                hornetq_template,
                app_path))
        log_file_path = self.log_file_path()
        log_file_dir = self.log_file_dir()
        os.system(
            '/bin/mkdir -p {} > /dev/null'.format(
                log_file_dir))
        os.system(
            '/bin/rm -f {} > /dev/null'.format(
                log_file_path))
        app_path = self._config['path']
        self._running = False
        os.system(
            'cd {}/bin && {}/bin/run.sh > {} &'.format(
                app_path,
                app_path,
                log_file_path))
        self.wait_for_startup()
        if (not self._running):
            raise Exception('timed out waiting for hornetq startup')
        return self

    def shutdown(self):
        app_path = self._config['path']
        self._running = True
        os.system(
            'cd {}/bin && {}/bin/stop.sh > /dev/null'.format(
                app_path,
                app_path))
        self.wait_for_shutdown()
        if (self._running):
            raise Exception('timed out waiting for hornetq shutdown')
        return self

    def wait_for_startup(self, timeout=60):
        self.wait_for_startup_message(timeout)

    def wait_for_startup_message(self, timeout=60):
        log_file_path = self.log_file_path()
        startup_msg = self._config['startup_msg']
        logging.debug('checking {} for startup message \'{}\''.format(log_file_path, startup_msg))
        for _ in range(timeout // 2):
            time.sleep(2)
            if self._checkLogForMessage(log_file_path, startup_msg):
                self._running = True
                logging.debug('found startup message')
                return
        logging.debug('failed to find startup message after {} seconds'.format(timeout))


    def _checkLogForMessage(self, log_file_path, desired_msg):
        found = False
        buffer = None
        try:
            buffer = open(log_file_path);
            if desired_msg in buffer.read():
                found = True
        except IOError:
            pass
        finally:
            if buffer is not None:
                buffer.close()
        return found

    def wait_for_shutdown(self, timeout=60):
        self.wait_for_shutdown_message(timeout)

    def wait_for_shutdown_message(self, timeout=60):
        log_file_path = self.log_file_path()
        msg = self._config['shutdown_msg']
        logging.debug('checking {} for shutdown message \'{}\''.format(log_file_path, msg))
        for _ in range(timeout // 2):
            time.sleep(2)
            if self._checkLogForMessage(log_file_path, msg):
                self._running = False
                logging.debug('found shutdown message')
                return
        logging.debug('failed to find shutdown message after {} seconds'.format(timeout))


    def log_file_dir(self):
        return '{}/{}'.format(self._config['path'],
                self._config['log_path'])

    def log_file_path(self):
        return '{}/{}/{}'.format(self._config['path'],
                self._config['log_path'],
                self._config['log_file'])
        
