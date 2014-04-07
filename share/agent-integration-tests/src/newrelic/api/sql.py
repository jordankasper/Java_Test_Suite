class SqlTrace:
    def __init__(self, fe_metric_name, uri, sql_id, sql, name,
                 num_calls, total_ms, min_ms, max_ms, params):

        self.fe_metric_name = fe_metric_name
        self.name = name
        self.uri = uri
        self.sql_id = sql_id
        self.sql = sql
        self.num_calls = num_calls
        self.total_ms = total_ms
        self.min_ms = min_ms
        self.max_ms = max_ms
        self.params = params

    @classmethod
    def parse_raw(cls, trace_data):
        return cls(*trace_data)

    def __repr__(self):
        return """<SQLTrace name:{}
 fe_metric_name:{}
 uri:{}
 sql_id:{}
 sql:{}
 num_calls:{}
 total_ms:{}
 min_ms:{}
 max_ms:{}
 params:{}>""".format(
           self.name,
           self.fe_metric_name,
           self.uri,
           self.sql_id,
           self.sql,
           self.num_calls,
           self.total_ms,
           self.min_ms,
           self.max_ms,
           self.params)
