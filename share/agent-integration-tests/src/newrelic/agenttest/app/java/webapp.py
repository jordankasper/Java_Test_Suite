import logging
import newrelic.agenttest.app
import os.path
import re
from subprocess import Popen, PIPE
import shutil

class WarApp(newrelic.agenttest.app.BaseApp):
    def __init__(self, config, test_env, **kwargs):
        super(WarApp, self).__init__(config, test_env)
        self._custom = kwargs.get('custom', {})
        self._teardown_files = []

    def _deploy(self):
        if self._test_env.get_var('custom_warfile_deploy'):
            self._custom_deploy_war(
                self._test_env.get_var('custom_warfile_deploy'))
        elif self._test_env.get_var('expand_warfile'):
            self._deploy_and_expand_war()
        else:
            self._deploy_war()

    def _custom_deploy_war(self, deploy):
        deploy(self._config['war_path'])

    def _deploy_war(self):
        war = self._config['war_path']
        logging.debug('deploying {} to {}'.format(war,
                self._test_env.get_var('webapp_path')))
        shutil.copy(war, self._test_env.get_var('webapp_path'))
        self._teardown_files.append(os.path.join(
                self._test_env.get_var('webapp_path'), os.path.basename(war)))

    def _deploy_and_expand_war(self):
        war = self._config['war_path']
        m = re.search('(.*)\.war$', os.path.basename(war))
        wardir = os.path.join(self._test_env.get_var('working_dir'),
                              m.group(1))
        if not os.path.exists(wardir):
            os.mkdir(wardir)

        logging.debug('deploying and expanding {} to {}'.format(
                war, self._test_env.get_var('webapp_path')))
        shutil.copy(war, wardir)
        os.system(
            'cd {} && {}/jar xfv {} > /dev/null'.format(
                wardir,
                self._test_env.get_var('java_bin'),
                war))

        link = os.path.join(self._test_env.get_var('webapp_path'), m.group(1))
        if os.path.lexists(link):
            os.unlink(link)

        logging.debug("linking {} to {}".format(wardir, link))
        os.symlink(wardir, link)
        self._teardown_files.append(link)

    def __enter__(self, *args):
        self._deploy()
        return self

    def __exit__(self, *args):
        self.shutdown()

    def startup(self):
        self._deploy()
        return self

    def shutdown(self):
        for f in self._teardown_files:
            try:
                os.unlink(f)
            except OSError as e:
                logging.warn(e)
        self._teardown_files = []

    def is_valid_config(self):
        return True

class MavenWarApp(WarApp):
    
    def startup(self):
        self._validate()
        self._build()
        self._deploy()
        return self
    
    def _validate(self):
        src = self._config['path']
        if not os.path.exists(src + '/pom.xml'): raise AssertionError
        war = self._config['war_path']
        if not war.startswith(src + '/target/'): raise AssertionError
        return self
    
    def _build(self):
        src = self._config['path']
        args = ['mvn', '-q', 'clean', 'package', '-DskipTests']
        for k in self._custom.keys():
            args.append('-D' + k + '=' + self._custom[k])
        p = Popen(args, cwd=src, stdout=PIPE, env={"PATH": os.environ.get('PATH'), "JAVA_HOME": self._test_env.get_var('java_home')})
        try:
            if p.wait() != 0:
                line = p.stdout.readline()
                while line:
                    print(line.decode(), end='')
                    line = p.stdout.readline()
                raise AssertionError
        finally:
            p.stdout.close()
        return self

class GrailsWarApp(WarApp):
    
    def startup(self):
        self._validate()
        self._build()
        self._deploy()
        return self
    
    def _validate(self):
        src = self._config['path']
        if not os.path.exists(src + '/application.properties'): raise AssertionError
        grails_home = self._config['grails_home']
        if not os.path.exists(grails_home + '/bin/grails'): raise AssertionError
        war = self._config['war_path']
        if not war.startswith(src + '/target/'): raise AssertionError
        return self
    
    def _build(self):
        src = self._config['path']
        grails_home = self._config['grails_home']
        logging.info("Grails Home: " + grails_home)
        self.runGrailsCommand(src, grails_home, 'clean')
        logging.info("Finished grails clean")
        self.runGrailsCommand(src, grails_home, 'war --stacktrace --verbose')
        logging.info("Finished grails war")
        return self

    def runGrailsCommand(self, src,grails_home, cmd):
        args = [grails_home + '/bin/grails', cmd]
        
        for k in self._custom.keys():
            args.append('-D' + k + '=' + self._custom[k])
        p = Popen(args, cwd=src, stderr=PIPE, env={"GRAILS_HOME": grails_home, "PATH": os.environ.get('PATH'), "JAVA_HOME": self._test_env.get_var('java_home')})
        try:
            if p.wait() != 0:
                line = p.stderr.readline()
                while line:
                    print(line.decode(), end='')
                    line = p.stderr.readline()
                #raise AssertionError("Error running grails command")
        finally:
            p.stderr.close()        
    

class TestWebapp(MavenWarApp):
    config_name = 'java_test_webapp'
    
class Spring32Webapp(WarApp):
    config_name = 'spring_mvc_showcase'
    
class Spring31Webapp(WarApp):
    config_name = 'spring_mvc_31_demo'
    
class Spring30Webapp(WarApp):
    config_name = 'spring_petclinic'
    
class QuartzWebapp(MavenWarApp):
    config_name = 'quartz_test'
    
class Grails1Webapp(GrailsWarApp):
    config_name = 'grails1_app'
    
class Grails2Webapp(GrailsWarApp):
    config_name = 'grails2_app'
