from .BaseViewerScene import BaseViewerScene
from src import constants


class LogsViewerScene(BaseViewerScene):
    def __init__(self, session, redis, driver):
        super().__init__()
        self.session = session
        self.redis = redis
        self.driver = driver

    def fetch(self, start, end):
        return self.redis.lrange(constants.LIST_ACTION_LOGS, start, end)

    def items_count(self):
        return self.redis.llen(constants.LIST_ACTION_LOGS)
