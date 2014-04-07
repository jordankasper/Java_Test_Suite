class BaseApp:
    def __init__(self, config, test_env, **kwargs):
        self._config = config
        self._test_env = test_env
        self._custom = kwargs.get('custom', {})

    @property
    def version(self):
        return self._config['version']

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        pass

    def startup(self):
        pass

    def shutdown(self):
        pass

    def is_valid_config(self):
        return True
