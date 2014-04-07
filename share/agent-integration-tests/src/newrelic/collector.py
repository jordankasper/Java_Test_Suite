import base64
import copy
import http.server
import inspect
import json
import logging
import newrelic.api.error
import newrelic.api.message
import newrelic.api.metric
import newrelic.api.event
import newrelic.api.profile
import newrelic.api.sql
import newrelic.api.module
import newrelic.api.transaction
import pprint
import re
import socketserver
import threading
import zlib
from newrelic.agenttest import obfuscator
from newrelic.agenttest.unittest import TestCase

class CollectorHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def _handle_request(self):
        m = re.search('method=([A-Za-z_]+)', self.path)
        if not m:
            logging.warn('no method param found:' + self.path)
        else:
            logging.debug('invoking handler for:' + m.group(1))
            self._handle_method(m.group(1))

    def _handle_method(self, method):
        self._METHOD_DISPATCH.get(method, self.__class__._do_unknown)(self)

    def _send_json_response_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _do_unknown(self):
        logging.warn('unknown method: ' + self.path)
        self.wfile.write(b'{"return_value":[]}')

    def _do_unimplemented(self):
        logging.warn('implement ' + inspect.stack()[1][4])
        self._send_json_response_headers()
        self.wfile.write(b'{"return_value":[]}')

    def _do_error_data(self):
        """ [agent_run_id, [errors]] """
        self._send_json_response_headers()
        (_, raw_errors) = self._decode_post()
        logging.debug(pprint.pformat(raw_errors))
        for error in raw_errors:
            self.server.errors.append(newrelic.api.error.Error.parse_raw(error))

    def _do_profile_data(self):
        """ [agent_run_id, [profiles]] """
        self._send_json_response_headers()
        (_, raw_profiles) = self._decode_post()
        logging.debug(pprint.pformat(raw_profiles))

        # In the agent some objects apply additional encoding and
        # compression to their internals before the library that sends
        # objects to New Relic does its own encoding and compresion.
        # As a result the responsibility for determining how to decode
        # and decompress an object is not cleanly encapsulated in one
        # place.  The decision was made to do all the decoding in this
        # class so the api classes can just convert data structures to
        # objects, but of course this means that this class knows a
        # bit too much about the internals of the incoming messages.

        for profile in raw_profiles:
            profile[4] = json.loads(
                zlib.decompress(base64.b64decode(profile[4].encode())).decode())
            self.server.profiles.append(newrelic.api.profile.Profile.parse_raw(profile))

        self.wfile.write(b'{"return_value":[]}')

    def _do_sql_trace_data(self):
        """
        the Java agent does not send an agent_run_id, just a list of sql_traces

        [sql_traces]
        """
        raw_sql_traces = self._decode_post()
        for trace in raw_sql_traces[0]:
            trace[9] = json.loads(
                zlib.decompress(base64.b64decode(trace[9].encode())).decode())
            self.server.sql_traces.append(newrelic.api.sql.SqlTrace.parse_raw(trace))

        logging.debug(pprint.pformat(raw_sql_traces))
        self.wfile.write(b'{"return_value":"null"}')
        
    def _do_load_modules(self):
        """
        The java agent does not send an agent_run_id, just a module type,  
        followed by a list of jars.
        
        [module_type, [jars]]
        
        where a jar is [name, version]
        """
        self._send_json_response_headers()
        (module_name, raw_modules) = self._decode_post()
        logging.debug(" Module Name: " + pprint.pformat(module_name))
        logging.debug("Modules: " + pprint.pformat(raw_modules))
        
        self.server.mod_name = module_name
        for mod in raw_modules:
            self.server.modules.append(newrelic.api.module.Module.parse_raw(mod))
           
        self.wfile.write(b'{"return_value":"null"}')
        
    def _do_analytic_event_data(self):
        """ [agent_run_id, [events]] """
        self._send_json_response_headers()
        (_, raw_events) = self._decode_post()
        logging.debug("Events: " + pprint.pformat(raw_events))
        
        for event in raw_events:
            self.server.events.append(newrelic.api.event.Event.parse_raw(event))
           
        self.wfile.write(b'{"return_value":"null"}')

    def _do_message_data(self):
        """ [agent_run_id, [messages]] """
        self._send_json_response_headers()
        (_, raw_messages) = self._decode_post()
        logging.debug(pprint.pformat(raw_messages))

        for message in raw_messages:
            self.server.messages.append(newrelic.api.message.Message.parse_raw(message))

        self.wfile.write(b'{"return_value":[]}')

    def _do_transaction_sample_data(self):
        """ [agent_run_id, [transaction_traces]] """
        self._send_json_response_headers()
        (_, raw_trans) = self._decode_post()
        for trans in raw_trans:
            trans[4] = json.loads(
                zlib.decompress(
                    base64.b64decode(trans[4].encode())).decode())
            self.server.transaction_traces.append(
                newrelic.api.transaction.TransactionTrace.parse_raw(trans))

        logging.debug(pprint.pformat(raw_trans))
        self.wfile.write(b'{"return_value":"null"}')

    def _do_get_redirect_host(self):
        self._send_json_response_headers()
        self.wfile.write(b'{"return_value":"localhost"}')

    def _do_shutdown(self):
        self._send_json_response_headers()
        self.wfile.write(b'{"return_value":[]}')

    def _do_get_agent_commands(self):
        self._send_json_response_headers()
        response = {'return_value' : self.server.command_options}
        self.wfile.write(json.dumps(response).encode())

    def _do_get_agent_command_results(self):
        self._send_json_response_headers()
        self.wfile.write(b'{"return_value":[]}')

    def _do_metric_data(self):
        """ [agent_run_id, begin_time, end_time, [metrics] """
        self._send_json_response_headers()
        (_, _, _, raw_metrics) = self._decode_post()
        logging.debug(pprint.pformat(raw_metrics))

        for metric in raw_metrics:
            self.server.metrics.append(newrelic.api.metric.Metric.parse_raw(metric))

        self.wfile.write(b'{"return_value":[]}')

    def _do_connect(self):
        self._send_json_response_headers()
        response = {'return_value' : self.server.connect_options}
        self.wfile.write(json.dumps(response).encode())

    def _do_queue_ping_command(self):
        self._do_unimplemented()

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _decode_post(self):
        data = self._get_post_data().decode('utf-8')
        return json.loads(data)

    def log_request(self, *args, **kwargs):
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            super(CollectorHTTPRequestHandler, self).log_request(
                *args, **kwargs)

    def log_message(self, fmt, *args, **kwargs):
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            super(CollectorHTTPRequestHandler, self).log_message(
                fmt, *args, **kwargs)

    def _get_post_data(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        if body and self.headers['Content-Encoding'].lower() == 'deflate':
            return zlib.decompress(body)
        else:
            return body

    _METHOD_DISPATCH = {
        'get_redirect_host'       : _do_get_redirect_host,
        'connect'                 : _do_connect,
        'shutdown'                : _do_shutdown,
        'metric_data'             : _do_metric_data,
        'transaction_sample_data' : _do_transaction_sample_data,
        'get_agent_commands'      : _do_get_agent_commands,
        'agent_command_results'   : _do_get_agent_command_results,
        'error_data'              : _do_error_data,
        'profile_data'            : _do_profile_data,
        'sql_trace_data'          : _do_sql_trace_data,
        'queue_ping_command'      : _do_queue_ping_command,
        'message_data'            : _do_message_data,
        'update_loaded_modules'   : _do_load_modules,
        'analytic_event_data'     : _do_analytic_event_data
    }


class CollectorHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):

    AGENT_ACCOUNT_ID = '54321'    
    AGENT_CROSS_PROCESS_ID = '54321#9876'
    CONNECT_OPTIONS = {
        'agent_config' : {
            'agent_enabled'                            : True,
            'log_level'                                : 'info',
            'audit_mode'                               : False,
            'capture_params'                           : True,
            'error_collector.enabled'                  : True,
            'error_collector.ignore_errors'            : [],
            'error_collector.ignore_status_codes'      : [404],
            'ignored_params'                           : [],
            'rum.load_episodes_file'                   : True,
            'slow_sql.enabled'                         : True,
            'thread_profiler.enabled'                  : True,
            'transaction_tracer.enabled'               : True,
            'transaction_tracer.explain_enabled'       : True,
            'transaction_tracer.explain_threshold'     : 0.5,
            'transaction_tracer.log_sql'               : False,
            'transaction_tracer.obfuscated_sql_fields' : [],
            'transaction_tracer.record_sql'            : 'raw',
            'transaction_tracer.stack_trace_threshold' : 0.5,
            'transaction_tracer.transaction_threshold' : 0.0050,
        },
        'apdex_t'           : 0.5,
        'agent_run_id'      : 1,
        'url_rules'         : [],
        'collect_errors'    : True,
        'cross_process_id'  : AGENT_CROSS_PROCESS_ID,
        'trusted_account_ids'  : [TestCase.ACCOUNT_ID, AGENT_ACCOUNT_ID],
        'encoding_key'      : obfuscator.ENCODING_KEY,
        'messages' : [{
                'message' : 'mock HTTP collector',
                'level'   : 'INFO'
        }],
        'sampling_rate'      : 0,
        'collect_traces'     : True,
        'data_report_period' : 60,
        'rum.enabled'        : True,
        'browser_key'        : '12345',
        'browser_monitoring.loader_version' : '248',
        'beacon'             : 'staging-beacon-2.newrelic.com',
        'error_beacon'       : 'staging-jserror.newrelic.com',
        'application_id'     : '45047',
        'js_agent_loader'    : 'window.NREUM||(NREUM={}),__nr_require=function a(b,c,d)',
        'js_agent_file'      : 'js-agent.newrelic.com\nr-248.min.js'
        
    }

    def __init__(self, addr, **kwargs):
        super(CollectorHTTPServer, self).__init__(
            addr, CollectorHTTPRequestHandler)

        self.metrics = []
        self.transaction_traces = []
        self.errors = []
        self.sql_traces = []
        self.profiles = []
        self.messages = []
        self.modules = []
        self.events = []
        self.mod_name = ""
        self._thread = None
        self._running = False
        self.command_options = kwargs.get('command_options', [])
        self.connect_options = self._merge_options(
            kwargs.get('connect_options', {}),
            self.CONNECT_OPTIONS)

    def _merge_options(self, custom, default):
        options = copy.deepcopy(default)
        options.update(custom)
        return options

    def __enter__(self, *args):
        self.startup()
        return self

    def __exit__(self, *args):
        self.shutdown()

    def startup(self):
        if not self._running:
            self._thread = threading.Thread(target = self.serve_forever)
            self._thread.daemon = True
            self._running = True
            self._thread.start()

    def shutdown(self):
        if self._running:
            super(CollectorHTTPServer, self).shutdown()
            self._running = False
            self.server_close()
            self._thread.join()
