class Metric:
    def __init__(self, name, scope, count, total_time, total_exclusive_time,
                 min_time, max_time, sum_of_squares):
        self.name = name
        self.scope = scope
        self.count = count
        self.total_time = total_time
        self.total_exclusive_time = total_exclusive_time
        self.min_time = min_time
        self.max_time = max_time
        self.sum_of_squares = sum_of_squares

    @classmethod
    def parse_raw(cls, raw_metric):
        return cls(
            name                 = raw_metric[0]['name'],
            scope                = raw_metric[0].get('scope', None),
            count                = raw_metric[1][0],
            total_time           = raw_metric[1][1],
            total_exclusive_time = raw_metric[1][2],
            min_time             = raw_metric[1][3],
            max_time             = raw_metric[1][4],
            sum_of_squares       = raw_metric[1][5])

    def __repr__(self):
        return"""<Metric name:{}
 scope:{}
 count:{}
 time:{}
 exclusive_time:{}
 min_time:{}
 max_time:{}
 sum_of_squares:{}>""".format(
            self.name,
            self.scope,
            self.count,
            self.total_time,
            self.total_exclusive_time,
            self.min_time,
            self.max_time,
            self.sum_of_squares)
