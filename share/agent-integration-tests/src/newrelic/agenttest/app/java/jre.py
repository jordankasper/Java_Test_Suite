import newrelic.agenttest.app
import os.path

class Java(newrelic.agenttest.app.BaseApp):
    config_name = 'java'

    def __init__(self, config, test_env, **kwargs):
        super(Java, self).__init__(config, test_env, **kwargs)
        test_env.set_var('java_home', config['path'])
        test_env.set_var('java_bin',
                         os.path.join(config['path'], config['bindir']))
