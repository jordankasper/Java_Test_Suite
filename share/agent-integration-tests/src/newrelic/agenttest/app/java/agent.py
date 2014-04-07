import newrelic.agenttest.app
import os.path
import shutil

# set the custom property use_metric_ext to run with the metric extension

class Agent(newrelic.agenttest.app.BaseApp):
    config_name = 'java_agent'
    
    def __init__(self, config, test_env, **kwargs):
        super(Agent, self).__init__(config, test_env)
        self._test_env.set_var(
            'javaagent',
            os.path.join(
                self._test_env.get_var('working_dir'),
                'newrelic.jar'))

        self.conf_path = config['config_template_path']
        self.jar_path = config['jar_path']
        self.ext_path = config['ext_path']
        self.metric_path = config['metric_path']
        self.use_metric_ext = False

        if self.conf_path is None:
            raise Exception('no config file specified')

        custom = kwargs.get('custom', {})
        if 'use_metric_ext' in custom:
            self.use_metric_ext = custom.get('use_metric_ext')

    def __enter__(self, *args):
        self.startup()
        return self

    def __exit__(self, *args):
        self.shutdown()
        
    def startup(self, with_metrics=False):
        shutil.copy(self.conf_path, self._test_env.get_var('working_dir'))
        
        extensions_path = os.path.join(self._test_env.get_var('working_dir'), 'extensions')
        self._make_ext_dir(extensions_path)
        shutil.copy(self.ext_path, extensions_path);   
        # only copy offer the metric extension if doing metrics testing   
        if self.use_metric_ext:
            shutil.copy(self.metric_path, extensions_path);

        shutil.copy(self.jar_path, os.path.join(self._test_env.get_var('working_dir'), 'newrelic.jar'))

    def _make_ext_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
