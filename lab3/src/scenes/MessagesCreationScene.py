from .BaseScene import BaseScene
from src import constants, Message


class MessageCreationScene(BaseScene):
    def __init__(self, session, redis, driver):
        super(MessageCreationScene, self).__init__([
            {
                'type': 'list',
                'name': 'to',
                'message': 'Who do you want to write to?',
                'choices': self.load_users
            },
            {
                'type': 'input',
                'name': 'body',
                'message': 'Enter your message',
                'default': lambda answers: 'Hi, %s' % answers['to']
            },
            {
                'type': 'confirm',
                'name': 'confirm',
                'message': 'Confirm?'
            }
        ])
        self.session = session
        self.redis = redis
        self.driver = driver

    def load_users(self, answers):
        return list(map(lambda v: ''.join(v.split(':')[1:]), self.redis.keys('%s:*' % constants.USERS_STORAGE)))

    def enter(self):
        answers = self.ask()
        if not answers['confirm']:
            return
        self.session['chat'].publish_message(
            Message(author=self.session['me'].login, to=answers['to'], body=answers['body']))
