import logging
from datetime import datetime
from time import time
import socket

class TestMetrics(object):

    def __init__(self, units):
        self._host_name = socket.gethostname()
        self._calendar_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')       
        self._servlet_metrics = {}
        self._units = units

    def _to_string(self):
        output = "METRICS: " + self._host_name + ":" + self._calendar_time + "\n" 
        for m in self._servlet_metrics.values():
            output += ' ' + m._to_string() + '\n'
        return output 
    
    def add_metric(self, servlet_name, report_type, test_name, framework, duration, iter_count, server, version, summarize):
        if (servlet_name in self._servlet_metrics):
            servlet = self._servlet_metrics[servlet_name]
            servlet.add_metric(test_name, framework, duration, iter_count, server, version)  
        else:
            servlet = ServerMetric(servlet_name, report_type, self._calendar_time, self._host_name, summarize, self._units)
            self._servlet_metrics[servlet_name] = servlet
            servlet.add_metric(test_name, framework, duration, iter_count, server, version)  
        
    def report_metric(self):
        for m in self._servlet_metrics.values():
            m.report_metric()
            
    def _summarize_metrics(self):
        output = ""
        for m in self._servlet_metrics.values():
            output += m.summarize_metrics()
        return output
    
    
    def write_metric_summary(self):
        output = self._summarize_metrics()
        if (len(output) > 0):
            logging.info("Summarizing metrics to file")
            file_out = open('/tmp/metrics_summary.txt', 'a')
            file_out.write('Metric Summary for ' + self._calendar_time + " on " + self._host_name + '\n' + output)
            file_out.close()
            
    def print_all_metrics(self):
        logging.info(self._to_string())
        
        
class ServerMetric(object):
    
    def __init__(self, servlet_name, report_type, calendar_time, host_name, summarize, units):
        self._report_type = report_type
        self._calendar_time = calendar_time
        self._host_name = host_name
        self._servlet_name = servlet_name 
        self._summarize = bool(summarize)
        self._test_metrics = {}
        self._units = units
        
    def _to_string(self):
        output = self._servlet_name + " : " + self._host_name + ":" + self._calendar_time + '\n'
        for m in self._test_metrics.values():
            output += '  ' + m._to_string() + '\n' 
        return output
    
    def _to_file_format(self):
        begin = self._servlet_name + "," + self._host_name + "," + self._calendar_time + ','
        output = ''
        for m in self._test_metrics.values():
            output +=  begin + m._to_file_format() + '\n' 
        return output
    
    def add_metric(self, test_name, framework, duration, iter_count, server, version):
        key = self.get_unique_key(framework, server, version)
        if key in self._test_metrics:
            #then just add the metric
            summary = self._test_metrics.get(key)
            summary.add_metric(test_name, duration)
        else:
            summary = ServerMetricUnit(framework, self._servlet_name, server, version, iter_count, self._units)
            self._test_metrics[key] = summary
            summary.add_metric(test_name, duration)
    
    def is_valid(self):
        if (self._servlet_name is None):
            logging.info("servlet name failed")
            return False
        elif (self._calendar_time is None):
            logging.info("calendar time failed")
            return False
        else:
            for m in self._test_metrics.values():
                if (m.is_valid is False):
                    return False 
            return True
        
    def report_metric(self):
        if (self.is_valid()):
            # report metric appropriately
            if (self._report_type == "DB"):
                logging.info("Sending metrics to database")
                self._write_to_file()
                logging.info("Please run the script bin/post_to_dashboard.rb")
            elif (self._report_type == "FILE"):
                logging.info("Sending metrics to file")
                self._write_to_file()
            else:
                logging.info("Printing metrics")
                logging.info(self._to_string());
        else:
            logging.info("Metric " + self._servlet_name + " is invalid and so is not being reported");
        
    def _write_to_file(self):
        file_out = open('/tmp/agent_metrics.txt', 'a')
        file_out.write(self._to_file_format())
        file_out.close()
        
    def get_unique_key(self, framework, server, version):
        return framework + "." + server + str(version)
        
    def summarize_metrics(self):
        if (self._summarize):
            output = ''
            for summary in self._test_metrics.values():
                output += '  ' + summary.get_summary()
            return output 
        else:
            return ''
        
        
class ServerMetricUnit(object):
    
    def __init__(self, framework, servlet, server, version, iter_count, units):
        self._framework = framework
        self._servlet = servlet
        self._iter_count = int(iter_count)
        self._server = server
        self._server_version = version
        self._iter_count = int(iter_count)
        self._disabled_duration = 0.0
        self._enabled_duration = 0.0
        self._logging_duration = 0.0
        self._units = units
        
    def add_metric(self, test_name, duration):
        if (test_name == 'disabled'):
            self._disabled_duration += float(duration)
        elif (test_name == 'enabled'):
            self._enabled_duration += float(duration)
        elif (test_name == 'enabled_logging'):
            self._logging_duration += float(duration)
        else: 
            logging.warning("Unknown test name. Not adding to summary. Name: " + test_name)
    
    def is_valid(self):
        if self._test_name is None:
            logging.info("test name failed")
            return False
        elif int(self._iter_count) < 1:
            logging.info("iter count failed")
            return False
        elif self._server is None:
            logging.info("server failed")
            return False
        elif self._server_version > 0:
            logging.info("version failed")
            return False
        else:
            return True
            
    def get_summary(self):
        output = "Test: " + self._framework + "." + self._servlet + " Server: " + self._server + " " + str(self._server_version) + "\n"
        enable_difference = self._enabled_duration - self._disabled_duration 
        log_difference = self._logging_duration - self._enabled_duration 
        output += "      Total(sec) for " + str(self._iter_count) + " Iterations: Dis: " + str(self._disabled_duration) + " En Added: " + str(enable_difference)
        output += " Log Added:" + str(log_difference) + "\n"
        disabled_per_dur = self._disabled_duration / self._iter_count
        enabled_per_dur = self._enabled_duration / self._iter_count
        enabled_per_diff = enabled_per_dur - disabled_per_dur
        logging_per_dur = self._logging_duration / self._iter_count
        logging_per_diff = logging_per_dur - enabled_per_diff
        output += "      Per Iteration(sec): Dis:" + str(disabled_per_dur) + ( "En Added: " + str(enabled_per_diff))
        output += " Log Added: " + str(logging_per_diff) + "\n"
        return output
    
    def _to_file_format(self):
        output = self._framework + "," + self._server + "," + str(self._server_version) + "," + str(self._iter_count)
        output += "," + self._units
        output +=  "," + str(self._disabled_duration) + "," + str(self._enabled_duration) + "," + str(self._logging_duration)
        return output
    
    def _to_string(self):
        output = self._framework + "," + self._server + "," + str(self._server_version) + "," + str(self._iter_count)
        output += "," + self._units
        output +=  "," + str(self._disabled_duration) + "," + str(self._enabled_duration) + "," + str(self._logging_duration)
        return output
