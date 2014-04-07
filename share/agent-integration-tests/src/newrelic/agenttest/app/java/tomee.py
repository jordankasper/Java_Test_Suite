from newrelic.agenttest.app.java.tomcat import Tomcat

class TomEE(Tomcat):
    config_name = 'tomee'

    def is_valid_config(self):
        if self.version >= 1.5:
            return self._test_env.java.version >= 6
        else:
            return True
