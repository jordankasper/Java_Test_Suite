class Event:
    def __init__(self, event_type, timestamp, name, duration, webDuration, user_params):
        self.event_type = event_type
        self.timestamp = timestamp
        self.name = name
        self.duration = duration
        self.webDuration = webDuration
        self.user_params = user_params

    @classmethod
    def parse_raw(cls, event_data):
        user_params = event_data[1] if len(event_data) > 1 else None
        return cls(event_data[0].get('type'), event_data[0].get('timestamp'), event_data[0].get('name'), event_data[0].get('duration'), event_data[0].get('webDuration'), user_params)

    def __repr__(self):
        return """<Event type:{} timestamp:{} name:{} duration:{} webDuration:{} user_params{}>""".format(self.event_type, self.timestamp, self.name, self.duration, self.webDuration, self.user_params)
