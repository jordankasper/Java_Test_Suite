import collections

class TransactionTrace:
    def __init__(self, start_ts, length_millis, name, uri, request_params, custom_params, segments, guid,
                 unused=None, force_persist=False):
        self.start_ts = start_ts
        self.length_millis = length_millis
        self.name = name
        self.uri = uri
        self.request_params = request_params
        self.custom_params = custom_params
        self._segments = segments
        self.guid = guid
        self.force_persist = force_persist

    @classmethod
    def parse_raw(cls, trace):
        request_params = trace[4][1]
        custom_params = trace[4][2]
        return cls(trace[0], trace[1], trace[2], trace[3], request_params, custom_params,
                   TransactionSegment.parse_raw(trace[4][3][4]), trace[5], trace[6], trace[7])

    @property
    def segments(self):
        segs = []
        to_visit = collections.deque(self._segments)
        while len(to_visit):
            s = to_visit.popleft()
            segs.append(s)
            ss = list(s.child_segments)
            ss.reverse()
            to_visit.extendleft(ss)

        return segs
    
    def get_property_count(self, property_name):
        count = 0
        for seg in self._segments:
            count += seg.get_property_count(property_name)
        return count

    def get_segs_with_prop(self, property_name):
        output = []
        for seg in self._segments:
            the_segs = seg.get_segs_with_prop(property_name)
            for current in the_segs:
                output.append(current)
        return output

    def __repr__(self):
        return"""<TransactionTrace name:{}
 start_ts:{}
 length:{}
 uri:{}
 segments:{}
 guid:{}
 force_persist:{}>""".format(
            self.name,
            self.start_ts,
            self.length_millis,
            self.uri,
            self._segments,
            self.guid,
            self.force_persist)

class TransactionSegment:
    def __init__(self, start_ts, end_ts, metric_name, params, child_segments,
                 class_name, method_name):
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.metric_name = metric_name
        self.params = params
        self.class_name = class_name
        self.method_name = method_name
        self.child_segments = child_segments

    @classmethod
    def parse_raw(cls, segments):
        return [
            cls(
                s[0], s[1], s[2], s[3],
                cls.parse_raw(s[4]), s[5], s[6])
            for s in segments]
        
    def get_property_count(self, property_name):
        segs = []
        count = 0
        segs.append(self);
        while(len(segs) > 0):
            current = segs.pop()
            if (property_name in current.params):
                count += 1
            for child in current.child_segments:
                segs.append(child)
            
        return count
    
    def get_segs_with_prop(self, property_name):
        output = []
        segs = []
        segs.append(self);
        while(len(segs) > 0):
            current = segs.pop()
            if (property_name in current.params):
                output.append(current)
            for child in current.child_segments:
                segs.append(child)
            
        return output

    def __repr__(self):
        return """<TransactionSegment metric_name:{}
 start_ts:{}
 end_ts:{}
 params:{}
 class_name:{}
 method_name:{}
 child_segments:{}>""".format(
            self.metric_name,
            self.start_ts,
            self.end_ts,
            self.params,
            self.class_name,
            self.method_name,
            self.child_segments)
