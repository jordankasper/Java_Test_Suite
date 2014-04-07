class Module:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    @classmethod
    def parse_raw(cls, module_data):
        return cls(*module_data)

    def __repr__(self):
        return """<Module name:{}
version:{}>""".format(
            self.name, self.version)