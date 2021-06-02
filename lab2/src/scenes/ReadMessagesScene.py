from .BaseScene import BaseScene
from src import constants
from pprint import pprint
from src import Message

BACK = 'Back'

ITEMS_PER_PAGE = 10
LOAD_NEW_PROMPT = [{
    'type': 'confirm',
    'name': 'continue',
    'message': 'Load new?',
}]


class ReadMessageScene(BaseScene):
    def __init__(self, session, redis):
        super().__init__([
            {
                'type': 'list',
                'name': 'mid',
                'message': 'What message do you want to read:',
                'choices': self.get_choices,
            }
        ])
        self.chat = session['chat']
        self.session = session
        self.redis = redis
        self.message = None
        self.queue_name = '%s:%s' % (constants.SS_INCOMING_MESSAGES, self.session['me'].login)

    def get_choices(self, *args):
        return [BACK, *self.get_messages()]

    def get_messages(self):
        return self.redis.zrange(self.queue_name, 0, self.redis.zcard(self.queue_name))

    def read_message(self, mid):
        message = Message.load(mid, self.redis)
        pprint(message.to_dict())
        if message.status != constants.STATUS_MESSAGE_READ:
            self.chat.read_message(message)

    def enter(self):
        self.clear()
        while True:
            answers = self.ask(clear=False)
            mid = answers['mid'] if 'mid' in answers else None
            if mid == BACK:
                return
            else:
                self.clear()
                self.read_message(mid)
