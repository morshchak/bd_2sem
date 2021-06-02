from .BaseViewerScene import BaseViewerScene
from src import constants


class OnlineUsersViewerScene(BaseViewerScene):
    def __init__(self, session, redis):
        super().__init__()
        self.session = session
        self.redis = redis

    def fetch(self, start, end):
        return list(map(lambda t: '"%s" with %i active sessions' % (t[0], t[1]),
                        self.redis.zrange(constants.SS_ONLINE_USERS, start, end, withscores=True)))

    def items_count(self):
        return self.redis.zcard(constants.SS_ONLINE_USERS)
