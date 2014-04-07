import operator
import functools

class Profile:
    def __init__(self, profile_id, start_time, end_time, sample_count,
                 profile_trees, thread_count, runnable_thread_count):
        self.profile_id = profile_id
        self.start_time = start_time
        self.end_time = end_time
        self.sample_count = sample_count
        self.profile_trees = profile_trees
        self.thread_count = thread_count
        self.runnable_thread_count = runnable_thread_count

    @classmethod
    def parse_raw(cls, profile_data):
        args = profile_data[0:4]
        profile_trees = {}
        args.append(profile_trees)
        args.extend(profile_data[5:])

        for profile_type, tree in profile_data[4].items():
            profile_trees[profile_type] = ProfileTree.parse_raw(tree)

        return cls(*args)

    def size(self):
        return functools.reduce(
            operator.add,
            map(lambda t: t.size(), self.profile_trees.values()),
            0)

    def __repr__(self):
        return """<Profile profile_id:{}
 start_time:{}
 end_time:{}
 sample_count:{}
 profile_trees:{}
 thread_count:{}
 runnable_thread_count:{}>""".format(
            self.profile_id,
            self.start_time,
            self.end_time,
            self.sample_count,
            self.profile_trees,
            self.thread_count,
            self.runnable_thread_count)

class ProfileTree:
    def __init__(self, cpu_time, segments):
        self.cpu_time = cpu_time
        self.segments = segments

    @classmethod
    def parse_raw(cls, tree_data):
        segments = []
        for data in tree_data[1:]:
            segments.append(ProfileSegment.parse_raw(data))

        return cls(
            tree_data[0]['cpu_time'],
            segments
        )

    def size(self):
        return functools.reduce(
            operator.add, map(lambda s: s.size(), self.segments), 0)

    def __repr__(self):
        return """<ProfileTree cpu_time:{}
 tree:{}
>""".format(self.cpu_time, self.segments)

class ProfileSegment:
    def __init__(self, method, runnable_call_count, non_runnable_call_count,
                 child_segments):
        self.method = method
        self.runnable_call_count = runnable_call_count
        self.non_runnable_call_count = non_runnable_call_count
        self.child_segments = child_segments

    @classmethod
    def parse_raw(cls, segment_data):
        child_segments = []
        for data in segment_data[3:]:
            if len(data) > 0:
                child_segments.append(cls.parse_raw(data[0]))

        return cls(
            ProfileMethod.parse_raw(segment_data[0]),
            segment_data[1],
            segment_data[2],
            child_segments)

    def size(self):
        return functools.reduce(
            operator.add, map(lambda s: s.size(), self.child_segments), 1)

    def __repr__(self):
        return """<ProfileSegment method:{}
 runnable_call_count:{}
 non_runnable_call_count:{}
 child_segments:{}>""".format(
            self.method,
            self.runnable_call_count,
            self.non_runnable_call_count,
            self.child_segments)

class ProfileMethod:
    def __init__(self, cls, method, line, instrumented=False):
        self.cls = cls
        self.method = method
        self.line = line
        self.instrumented = instrumented

    @classmethod
    def parse_raw(cls, method_data):
        return cls(*method_data)

    def __repr__(self):
        return """<ProfileMethod class:{}
 method:{}
 line:{}>""".format(self.cls, self.method, self.line)
