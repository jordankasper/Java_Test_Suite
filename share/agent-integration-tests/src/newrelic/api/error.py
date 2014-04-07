class Error:
    def __init__(self, ts, path, message, exception_type, params):
        self.ts = ts
        self.path = path
        self.message = message
        self.exception_type = exception_type
        self.params = params

    @classmethod
    def parse_raw(cls, error_data):
        return cls(*error_data)

    def __repr__(self):
        return """<Error ts:{}
 path:{}
 message:{}
 exception_type:{}
 params:{}>""".format(
            self.ts, self.path, self.message, self.exception_type,
            self.params)
