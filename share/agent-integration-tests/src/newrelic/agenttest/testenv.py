import collections
import logging
import os
import pprint
import shutil
import tempfile
import yaml
import sys

class TestEnv:
    def __init__(self, conf_path, custom_path, stoplist_path):
        self._working_dir = tempfile.mkdtemp(dir = '/tmp')
        self._running = False
        self._env = {}
        self._apps = collections.OrderedDict()
        self.set_var('working_dir', self._working_dir)
        logging.info('working_dir: ' + self._working_dir)

        # Process the stop list. Note the test framework is used for non-test scripts, such as reposync.py
        # When used this way, the stoplist_path will be None. So we check. And we predeclare the var for these cases.

        self.stoplist = []
        if stoplist_path:
            try:
                with open(stoplist_path, 'r') as f:
                    self.stoplist = yaml.load(f)
            except IOError:
                logging.info('Stoplist file not found or invalid: ' + stoplist_path)
                logging.info('All tests will be executed.')

        with open(conf_path, 'r') as f:
            conf = yaml.load(f)['config']

        with open(custom_path, 'r') as f:
            cust = yaml.load(f)
            var = cust.get('var', {})
            override = cust.get('override', {})

        self.config = self._expand_vars(conf, var or {})
        self._set_overrides(self.config, override or {})

    def _expand_vars(self, conf, var):
        if isinstance(conf, str):
            return self._expand_var(conf, var)
        elif isinstance(conf, dict):
            expanded = {}
            for (k, v) in conf.items():
                v = self._expand_vars(v, var)
                expanded[k] = v
            return expanded
        elif isinstance(conf, list):
            expanded = []
            for e in conf:
                expanded.append(self._expand_vars(e, var))
            return expanded
        else:
            return conf

    def _expand_var(self, conf, var):
        expandvar = ''
        expandstr = ''
        inexpand = False
        for i in range(len(conf)):
            if conf[i] == '(' and i > 0 and conf[i - 1] == '$':
                inexpand = True
            elif conf[i] == ')':
                expandstr += var[expandvar]
                expandvar = ''
                inexpand = False
            elif inexpand:
                expandvar += conf[i]
            elif conf[i] != '$':
                expandstr += conf[i]

        return expandstr

    def _set_overrides(self, conf, override):
        for (key, val) in override.items():
            path = key.split('.')
            self._set_override(conf, path, val)

    def _set_override(self, conf, path, val):
        if len(path) == 1:
            if path[0] in conf:
                conf[path[0]] = val
            else:
                raise Exception('unable to find override {} in config'.format(path[0]))
        else:
            first = path[0]
            rest = path[1:]
            if first.find('=') == -1:
                self._set_override(conf[first], rest, val)
            else:
                (k, v) = first.split('=')
                for c in conf:
                    if k in c and str(c[k]) == v:
                        self._set_override(c, rest, val)
                        break
                else:
                    raise Exception(
                        'unable to find override {} in config'.format(first))

    def _filter_property(self, conf, **filters):
        if isinstance(conf, list) and filters:
            for elem in conf:
                for attribute in elem.keys():
                    if attribute in filters and filters[attribute] == elem[attribute]:
                        return elem
        return conf

    def get_property(self, prop, **filters):
        parts = prop.split('.')
        conf = self.config

        for p in parts:
            conf = self._filter_property(conf, **filters)
            try:
                conf = conf[p]
            except Exception as e:
                logging.warn(pprint.pformat([p, conf, filters]))
                raise(e)

        prop = self._filter_property(conf, **filters)
        if isinstance(prop, str):
            return prop.format_map(self._variables)

        return prop

    def register_app(self, name, app):
        setattr(self, name, app)
        self._apps[name] = app

    def unregister_app(self, name):
        self._apps.pop(name)

    def get_app(self, name):
        return self._apps[name]

    def set_var(self, var, val):
        self._env[var] = val

    def get_var(self, var, default_value=None):
        return self._env.get(var, default_value)

    def startup(self):
        apps = []
        failure = None
        self._running = True

        for name, app in self._apps.items():
            try:
                logging.debug('starting app {}'.format(name))
                app.startup()
                apps.append(app)
            except Exception as e:
                failure = e
            finally:
                if failure:
                    try:
                        for a in apps:
                            a.shutdown()
                    except:
                        pass
            if failure:
                raise failure

    def shutdown(self):
        if self._running:
            errors = []
            for app in self._apps.values():
                try:
                    app.shutdown()
                except Exception as e:
                    errors.append(e)

            if errors:
                raise errors[0]
            self._running = False

    def is_valid_config(self):
        for app in self._apps.values():
            if not app.is_valid_config():
                logging.debug('app claimed invalid config:' + app.config_name)
                return False
        return True

    def cleanup(self):
        self.shutdown()
        if not os.environ.get('TEST_SAVE_WORKDIR', False):
            shutil.rmtree(self._working_dir)
