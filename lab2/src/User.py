from src import constants


class User:
    def __init__(self, login, role, redis):
        self.login = login
        self.role = role
        self.redis = redis
        p = self.redis.pipeline()
        p.lpush(constants.LIST_ACTION_LOGS, 'user "%s" login' % self.login)
        p.zincrby(constants.SS_ONLINE_USERS, 1, self.login)
        p.execute()

    def save(self):
        p = self.redis.pipeline()
        p.hmset('%s:%s' % (constants.USERS_STORAGE, self.login), {'login': self.login, 'role': self.role})
        p.execute()

    @staticmethod
    def load(redis, login):
        user = redis.hgetall('%s:%s' % (constants.USERS_STORAGE, login))
        if not user:
            return None
        return User(user['login'], user['role'], redis)

    def __del__(self):
        p = self.redis.pipeline()
        p.lpush(constants.LIST_ACTION_LOGS, 'user "%s" logout' % self.login)
        p.zincrby(constants.SS_ONLINE_USERS, -1, self.login)
        results = p.execute()
        if not results[1]:
            self.redis.zrem(constants.SS_ONLINE_USERS, self.login)
