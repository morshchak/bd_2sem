from src import constants
import time


class Message:
    def __init__(self, author, to, body, created_at=int(round(time.time() * 1000)),
                 status=constants.STATUS_MESSAGE_CREATED,
                 id=None):
        self.author = author
        self.to = to
        self.body = body
        self.status = status
        self.created_at = created_at
        self.id = id or self.get_id()

    def get_id(self):
        return '%s:%s:%i' % (self.author, self.to, self.created_at)

    def to_dict(self):
        return {
            'body': self.body,
            'to': self.to,
            'author': self.author,
            'status': self.status,
            'id': self.id,
            'created_at': self.created_at
        }

    def save(self, redis):
        redis.hmset('%s:%s' % (constants.MESSAGES_STORAGE, self.id), self.to_dict())

    @staticmethod
    def load(mid, redis):
        serialized_message = redis.hgetall('%s:%s' % (constants.MESSAGES_STORAGE, mid))
        if not serialized_message:
            return None
        return Message(**serialized_message)
