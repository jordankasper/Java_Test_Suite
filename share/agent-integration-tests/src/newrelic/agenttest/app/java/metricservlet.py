import newrelic.agenttest.app

class Servlet(newrelic.agenttest.app.BaseApp):
    config_name = 'metric_servlet'

    def __init__(self, config, test_env, **kwargs):
        super(Servlet, self).__init__(config, test_env, **kwargs)
        self.name = config['name']
        self.iter_count = config['iter_count']
        self.method_count = config['method_count']
        self.report_type = config['report_type']
        self.repeat_count = config['repeat_count']
        self.summary = config['summary']

    def get_name(self):
        return self.name
    
    def get_iter_count(self):
        return self.iter_count
    
    def get_report_type(self):
        return self.report_type
    
    def get_repeat_count(self):
        return self.repeat_count
    
    def is_summary(self):
        return bool(self.summary)
    
    def get_method_count(self):
        return self.method_count