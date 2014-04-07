import logging
import os
import re
import traceback
import types

__all__ = ['app_decorator']

def _app_runner(cls):
    def __app_runner(test_suite, test_method, *args, **kwargs):

        select = _select_overrides(cls) or kwargs.get('select', {})

        for app_conf in _select_configs(cls, test_suite.test_env, **select):
            app = cls(app_conf, test_suite.test_env, **kwargs)
            test_suite.test_env.register_app(app.config_name, app)

            level = '.' * len(traceback.extract_stack())
            if test_suite.test_env.is_valid_config():
                logging.info(level + ' {} [{}]'.format(
                    cls.config_name, app_conf['version']))
                if not hasattr(test_method, '_test_decorator'):
                    try:
                        test_suite.test_env.startup()
                        test_method(test_suite)
                    finally:
                        test_suite.test_env.shutdown()
                else:
                    test_method(test_suite)
            else:
                logging.info(
                    '{} {} [{}: SKIPPING - invalid env combination]'
                    .format(level, cls.config_name, app_conf['version']))
            test_suite.test_env.unregister_app(app.config_name)
    return __app_runner

def _select_overrides(cls):
    if 'TEST_APP_OVERRIDE' not in os.environ:
        return

    for select_str in os.environ['TEST_APP_OVERRIDE'].split(','):
        (select_key, val) = select_str.split('=')
        (select_name, key) = select_key.split('.')
        m = re.match('^(\d+)(\.\d+)?$', val)
        if m:
            val = len(m.groups()) == 2 and float(val) or int(val)

        if select_name == cls.config_name:
            return {key : val}

def _select_configs(cls, test_env, **select):
    if not select:
        return filter(
            lambda conf: conf.get('default', True),
            test_env.get_property(cls.config_name))
    else:
        configs = []
        for key, vals in select.items():
            if not isinstance(vals, list):
                vals = [vals]

            for val in vals:
                configs.append(
                    test_env.get_property(cls.config_name, **{key : val}))

        return configs

def _init_test_decorator(decorator, function):
    # set the wrapper function name to that of the underlying function
    # so that the unittest framework can use the __name__ attribute
    # to lookup the wrapped function by name
    decorator.__name__ = function.__name__
    # set a flag to differenciate a test decorator from the actual test
    setattr(decorator, '_test_decorator', True)
    return decorator

def _app_decorator(app):
    """
    returns a decorator function for the given app runner function
    """
    def __app_decorator(*args, **kwargs):
        if len(args) and type(args[0]) is types.FunctionType:
            return _init_test_decorator(
                lambda test_suite: app(test_suite, args[0]), args[0])
        else:
            def app_filter_decorator(test_method):
                return _init_test_decorator(
                    lambda test_suite:
                        app(test_suite, test_method, *args, **kwargs),
                    test_method)
            return app_filter_decorator

    return __app_decorator

def app_decorator(cls):
    return _app_decorator(_app_runner(cls))
