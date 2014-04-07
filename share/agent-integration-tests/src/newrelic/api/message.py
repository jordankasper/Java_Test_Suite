class Message:
    def __init__(self, title, message, severity):
        self.title = title
        self.message = message
        self.severity = severity

    @classmethod
    def parse_raw(cls, raw_message):
        return cls(**raw_message)#msg['title'], msg['message'], msg['severity'])

    def __repr__(self):
        return"""<Message name:{}
 title:{}
 message:{}
 severity:{}>""".format(
            self.title,
            self.message,
            self.severity)
