from src import constants, Message
import time


def now():
    return int(round(time.time() * 1000))


class Chat:
    def __init__(self, redis, driver):
        self.redis = redis
        self.driver = driver

    def close(self):
        self.driver.close()

    @staticmethod
    def _sent_message(tx, message):
        result = tx.run("MATCH (recipient:User{login: $recipient})"
                        "MATCH (sender:User{login: $sender})"
                        "CREATE (message:Message{body: $body, mess_id: $id})"
                        "CREATE (sender)-[:SENT]->(message)"
                        "CREATE (message)-[:WAS_SENT_TO]->(recipient)",
                        sender=message.author, recipient=message.to, id=message.id, body=message.body)
        return result

    @staticmethod
    def _read_message(tx, message):
        result = tx.run("MATCH (recipient:User{login: $recipient})"
                        "MATCH (message:Message{body: $body, mess_id: $id})"
                        "MERGE (message)-[:WAS_READ_BY]->(recipient)",
                        recipient=message.to, id=message.id, body=message.body)
        return result

    @staticmethod
    def _block_message(tx, message, admin_log):
        result = tx.run("MATCH (admin:User{login: $admin_log})"
                        "MATCH (message:Message{mess_id: $id})"
                        "MERGE (admin)-[:BLOCKED]->(message)",
                        admin_log=admin_log, id=message.id)
        return result

    @staticmethod
    def _approve_message(tx, message, admin_log):
        result = tx.run("MATCH (admin:User{login: $admin_log})"
                        "MATCH (message:Message{mess_id: $id})"
                        "MERGE (admin)-[:APPROVED]->(message)",
                        admin_log=admin_log, id=message.id)
        return result

    @staticmethod
    def _message_send_by(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]

    def publish_message(self, message):
        s = self.driver.session()
        p = self.redis.pipeline()
        message.save(p)
        p.publish('%s:%s' % (constants.EVENT_MESSAGE_CREATED, message.author), message.id)
        p.sadd(constants.SET_UNPROCESSED_MESSAGES, message.id)
        p.zadd('%s:%s' % (constants.SS_SENT_MESSAGES, message.author), {message.id: now()})
        p.zadd('%s:%s' % (constants.SS_WAIT_FOR_MODERATION_MESSAGES, message.author), {message.id: now()})
        p.lpush(constants.LIST_ACTION_LOGS, 'user "%s" publish message "%s"' % (message.author, message.id))
        p.execute()
        s.write_transaction(self._sent_message, message)

    def listen_events(self, events_handlers):
        p = self.redis.pubsub()
        p.psubscribe(**events_handlers)
        thread = p.run_in_thread(sleep_time=0.001)
        return thread

    def get_next_unprocessed_message(self, admin_login):
        mid = self.redis.srandmember(constants.SET_UNPROCESSED_MESSAGES, 1)
        if not mid or not mid[0]:
            return
        mid = mid[0]
        message_key = '%s:%s' % (constants.MESSAGES_STORAGE, mid)
        author = self.redis.hget(message_key, 'author')
        message = Message.load(mid, self.redis)
        p = self.redis.pipeline()
        p.srem(constants.SET_UNPROCESSED_MESSAGES, mid)
        p.zrem('%s:%s' % (constants.SS_WAIT_FOR_MODERATION_MESSAGES, author), mid)
        message.status = constants.STATUS_MESSAGE_ON_MODERATION
        message.save(p)
        p.zadd('%s:%s' % (constants.SS_MESSAGES_ON_MODERATION, author), {mid: now()})
        p.lpush(constants.LIST_ACTION_LOGS, '"%s" took message "%s" on moderation' % (admin_login, mid))
        p.execute()
        return message

    def approve_message(self, admin_login, message):
        p = self.redis.pipeline()
        s = self.driver.session()
        message.status = constants.STATUS_MESSAGE_APPROVED
        message.save(p)
        p.srem(constants.SET_UNPROCESSED_MESSAGES, message.id)
        p.lpush(constants.LIST_ACTION_LOGS, 'admin "%s" approve message "%s"' % (admin_login, message.id))
        p.zrem('%s:%s' % (constants.SS_MESSAGES_ON_MODERATION, message.author), message.id)
        p.zadd('%s:%s' % (constants.SS_APPROVED_MESSAGES, message.author), {message.id: now()})
        p.zincrby(constants.SS_ACTIVE_SENDERS, 1, message.author)
        p.zadd('%s:%s' % (constants.SS_INCOMING_MESSAGES, message.to), {message.id: message.created_at})
        p.publish('%s:%s' % (constants.EVENT_MESSAGE_APPROVED, message.author), message.id)
        p.publish('%s:%s' % (constants.EVENT_INCOMING_MESSAGE, message.to), message.id)
        p.execute()
        s.write_transaction(self._approve_message, message, admin_login)

    def block_message(self, admin_login, message):
        p = self.redis.pipeline()
        s = self.driver.session()

        message.status = constants.STATUS_MESSAGE_BLOCKED
        message.save(p)
        p.srem(constants.SET_UNPROCESSED_MESSAGES, message.id)
        p.zrem('%s:%s' % (constants.SS_MESSAGES_ON_MODERATION, message.author), message.id)
        p.zadd('%s:%s' % (constants.SS_BLOCKED_MESSAGES, message.author), {message.id: now()})
        p.zincrby(constants.SS_SPAMMERS, 1, message.author)
        p.publish('%s:%s' % (constants.EVENT_MESSAGE_BLOCKED, message.author), message.id)
        p.lpush(constants.LIST_ACTION_LOGS, 'admin "%s" block message "%s"' % (admin_login, message.id))
        p.execute()
        s.write_transaction(self._block_message, message, admin_login)

    def read_message(self, message):
        if not message:
            return
        p = self.redis.pipeline()
        s = self.driver.session()
        message.status = constants.STATUS_MESSAGE_READ
        message.save(p)
        p.zrem('%s:%s' % (constants.SS_APPROVED_MESSAGES, message.author), message.id)
        p.sadd('%s:%s' % (constants.SET_READ_MESSAGES, message.to), message.id)
        p.zadd('%s:%s' % (constants.SS_DELIVERED_MESSAGES, message.author), {message.id: now()})
        p.lpush(constants.LIST_ACTION_LOGS, 'user "%s" read message "%s"' % (message.to, message.id))
        p.publish('%s:%s' % (constants.EVENT_MESSAGE_DELIVERED, message.author), message.id)
        p.execute()
        s.write_transaction(self._read_message, message)
