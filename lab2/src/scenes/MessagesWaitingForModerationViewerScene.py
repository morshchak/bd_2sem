from .BaseViewerScene import BaseViewerScene
from src import constants


class WaitForModerationMessagesViewerScene(BaseViewerScene):
    def __init__(self, session, redis):
        super().__init__()
        self.session = session
        self.redis = redis

    def fetch(self, start, end):
        return self.redis.zrange('%s:%s' % (constants.SS_WAIT_FOR_MODERATION_MESSAGES, self.session['me'].login), start, end)

    def items_count(self):
        return self.redis.zcard('%s:%s' % (constants.SS_WAIT_FOR_MODERATION_MESSAGES, self.session['me'].login))
