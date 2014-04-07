from copy import copy
from newrelic.agenttest import obfuscator
import configparser
import itertools
import logging
import newrelic.agenttest.testenv
import os
import re
import unittest
import warnings

class TestCase(unittest.TestCase):
    
    ACCOUNT_ID = 12345
    CROSS_PROCESS_ID = '12345#6789'
    OBFUSCATED_CROSS_PROCESS_ID = obfuscator.obfuscate(CROSS_PROCESS_ID)

    def assertInstrumentation(self, expected):
        names = copy(self.test_env.config['instrumentation_assert'][0]['names'])
        for k in expected.keys():
            if k not in names:
                raise AssertionError(k + " not a configured instrumentation package (add to instrumentation_assert in java_config.yml).")
            names.remove(k)
        
        loaded_metrics = list(map(lambda m: re.search("Supportability/WeaveInstrumentation/Loaded/([^/]+)/", m.name).group(1),
                filter(
                    lambda m: m.name.startswith('Supportability/WeaveInstrumentation/Loaded') and m.scope is None,
                    self.test_env.collector._get_all_unscoped_metrics())))
        skipped_metrics = list(map(lambda m: re.search("Supportability/WeaveInstrumentation/Skipped/([^/]+)/", m.name).group(1),
                filter(
                    lambda m: m.name.startswith('Supportability/WeaveInstrumentation/Skipped') and m.scope is None,
                    self.test_env.collector._get_all_unscoped_metrics())))

        if not (loaded_metrics or skipped_metrics):
                raise AssertionError("no instrumentation loaded or skipped.")

        for k in expected.keys():
            if expected[k]:
                if not self._string_matches_list(k, loaded_metrics):
                    raise AssertionError(k + " not found in loaded instrumentation.")
            else:
                if not self._string_matches_list(k, skipped_metrics):
                    raise AssertionError(k + " not found in skipped instrumentation.")

        for k in names:
            if self._string_matches_list(k, loaded_metrics):
                raise AssertionError(k + " loaded unexpectedly.")
    
    def assertMatchesPattern(self, actual, pattern):
        compiled_p = re.compile(pattern)
        self.assertTrue(compiled_p.search(actual), "The pattern " + pattern + " does not match actual:\n" + actual)
    
    def _string_matches_list(self, name, metrics_list):
        for val in metrics_list:
            if val.endswith(name):
                return True
        return False

    def assertAttrEqual(self, obj, **attrs):
        for (attr, val) in attrs.items():
            self.assertEqual(val, getattr(obj, attr))
            
    def assertStringEqual(self, actual, expected):
        self.assertEqual(expected, actual)
        
    def assertNotNull(self, obj):
        self.assertTrue("The object is null.", obj is not None)
        
    def assertNull(self, obj):
        self.assertTrue("The object is not null.", obj is None)
        
    def assertValueAtleast(self, objs, *expect_attrs, **attr_comps):
        idx = 0
        for (obj, attrs) in itertools.zip_longest(objs, expect_attrs):
            for (attr, val) in attrs.items():
                if attr in attr_comps:
                    attr_comps[attr](
                        getattr(obj, attr),
                        val,
                        msg='objects[{}].{}'.format(idx, attr))
                else:
                    self.assertGreaterEqual(
                        getattr(obj, attr), val,
                        msg='objects[{}].{} expected {}, actual {}'.format(
                            idx, attr, val, getattr(obj, attr)))
            idx += 1
            
    def returnFirstExpectedAttrVal(self, objs, *expect_attr):
        idx = 0
        for (obj, attrs) in itertools.zip_longest(objs, expect_attr):
            for attr in attrs:
                return getattr(obj, attr)
            idx += 1
        return 0
    
        
    def assertIterAttributes(self, objs, *attrs, **attr_comps):
        obj_list = list(objs)
        attr_list = list(attrs)
        self.removeMatches(obj_list, attr_list, **attr_comps)
        if len(obj_list) == 0 and len(attr_list) == 0:
            return
        msgs = []
        for obj in obj_list:
            msg='Did not expect {}'.format(obj)
            msgs.append(msg)
            msgs.append('\n')
        for attr in attr_list:
            if attr_comps == None or len(attr_comps) == 0:
                msg='Expected {}'.format(attr)
                msgs.append(msg)
                msgs.append('\n')
            else:
                msg='Expected {} {}'.format(attr, attr_comps)
                msgs.append(msg)
                msgs.append('\n')
        self.fail(''.join(msgs))

    def removeMatches(self, obj_list, attr_list, **attr_comps):
        """Remove objs that match an attr."""
        obj_list[:] = [obj for obj in obj_list if not self.removeAttrMatches(obj, attr_list, **attr_comps)]
    
    def removeAttrMatches(self, obj, attr_list, **attr_comps):
        """Return True if the obj matches an attr"""
        for attr in attr_list:
            """Remove first attr that matches the obj."""
            if self.matchesAttr(obj, attr, **attr_comps):
                attr_list.remove(attr)             
                return True
        return False
    
    def matchesAttr(self, obj, attr, **attr_comps):
        """Return True if the obj matches the attr."""
        for item in attr.items():
            expect_val = item[1]
            actual_val = getattr(obj, item[0])
            attr_comp = attr_comps.get(item[0])
            if attr_comp == None:
                if actual_val != expect_val:
                    return False
            else:
                attr_comp(
                    actual_val,
                    expect_val)
        return True
    
    def assertDictContainsSubset(self, d, ss, *args):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            super(TestCase, self).assertDictContainsSubset(d, ss, *args)
            
    def assertSegmentPropCount(self, transation_traces, property_name, property_count):
        for tt in transation_traces:
            self.assertEqual(property_count, tt.get_property_count(property_name), "The number of transaction segments with property " + property_name + " did not equal " + str(property_count))        

    def aggregate_by(self, lst, key, attr):
        res = {}
        for e in lst:
            k = getattr(e, key)
            v = getattr(e, attr)
            if k in res:
                res[k][attr] += v
            else:
                res[k] = {key : k, attr : v}
        return res

    def tearDown(self):
        self.test_env.cleanup()
        self.test_env = None

    def setUp(self):
        self.test_env = newrelic.agenttest.testenv.TestEnv(
            os.environ['TEST_CONFIG'],
            os.environ['TEST_LOCAL_CONFIG'],
            os.environ.get('AIT_STOP_LIST', None))

        # Process the stop list. It is a dictionary of lists keyed by test file name
        # Each value is a list containing the methods to skip in that file name
        # The name of "this" (currently executing) test file is stashed in os.environ.
        # The name of the method we're setting up for is in self._testMethodName.

        test_file = os.environ.get('_AIT_INTERNAL_TESTPATH_', '?')
        method_name = self._testMethodName
        logging.debug('setUp(): test file: {0} method: {1} stoplist: {2}'.format(test_file, method_name, self.test_env.stoplist))
        if (test_file in self.test_env.stoplist) and (method_name in self.test_env.stoplist[test_file]):
            self.skipTest('{0}:{1} - found in stop list'.format(test_file, method_name))

def initenv(test_file):
    # Record the test_file for use by the setUp() override.
    os.environ.setdefault('_AIT_INTERNAL_TESTPATH_', test_file)

    # I think this is stale code that doesn't do anything.
    # This is NOT the code that processes our .yml files.

    paths = [os.path.abspath(test_file)]
    test_conf = os.environ.get('TEST_CONFIG', None)
    test_local_conf = os.environ.get('TEST_LOCAL_CONFIG', None)

    while paths and not (test_conf or test_local_conf):
        paths = os.path.split(paths[0])
        conf = os.path.join(paths[0], 'test.ini')
        if os.path.exists(conf):
            parser = configparser.ConfigParser()
            parser.read(conf)
            test_conf = parser['config']['TEST_CONFIG']
            test_local_conf = parser['config']['TEST_LOCAL_CONFIG']
            break
    else:
        return

    paths = [os.path.abspath(test_file)]
    while paths and not ('TEST_CONFIG' in os.environ or 'TEST_LOCAL_CONFIG' in os.environ):
        paths = os.path.split(paths[0])
        tc = os.path.join(paths[0], 'conf', test_conf)
        if os.path.exists(tc):
            os.environ.setdefault('TEST_CONFIG', tc)
        tlc = os.path.join(paths[0], 'conf', test_local_conf)
        if os.path.exists(tlc):
            os.environ.setdefault('TEST_LOCAL_CONFIG', tlc)


def main():
    logging.getLogger().setLevel(os.environ.get('TEST_LOG_LEVEL', 'INFO'))
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s')
    unittest.main()
