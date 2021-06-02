from .BaseViewerScene import BaseViewerScene
from src import constants


class SentMessagesViewerScene(BaseViewerScene):
    def __init__(self, session, redis):
        super().__init__()
        self.session = session
        self.redis = redis
        self.key = '%s:%s' % (constants.SS_SENT_MESSAGES, self.session['me'].login)

    def fetch(self, start, end):
        messages = self.redis.zrange(self.key, start, end)
        return list(map(self.map_messages_statuses, messages))

    def items_count(self):
        return self.redis.zcard(self.key)

    def map_messages_statuses(self, mid):
        status = self.redis.hget('%s:%s' % (constants.MESSAGES_STORAGE, mid), 'status')
        if status == constants.STATUS_MESSAGE_BLOCKED:
            return '"%s" %s' % (mid, status)
        elif status == constants.STATUS_MESSAGE_APPROVED:
            return '"%s" %s' % (mid, status)
        else:
            return '"%s" %s' % (mid, status)
