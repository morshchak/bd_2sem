from .BaseScene import BaseScene
from .UserActionsScene import UserActionsScene
from src import constants, User, Message
from PyInquirer import ValidationError, Validator
from random import random

WORKER = 'I am a worker'
USER = 'I am a user'
EXIT = 'Exit'


class LoginValidator(Validator):
    def validate(self, document):
        if not len(str(document.text).strip()):
            raise ValidationError(
                message='Login cannot be empty',
                cursor_position=len(document.text))


class GreetingScene(BaseScene):
    def __init__(self, session, redis):
        super().__init__([
            {
                'type': 'list',
                'name': 'role',
                'message': 'Choose what you want',
                'choices': [
                    WORKER,
                    USER,
                    EXIT
                ]
            },
            {
                'type': 'input',
                'name': 'login',
                'message': 'Your login',
                'when': lambda answers: answers['role'] == USER,
                'validate': LoginValidator
            }
        ])
        self.redis = redis
        self.chat = session['chat']
        self.thread = None
        self.session = session

    def enter_as_worker(self):
        self.session['role'] = constants.WORKER_ROLE
        self.thread = self.chat.listen_events({
            '%s:*' % constants.EVENT_MESSAGE_CREATED: self.handle_message_created_as_worker
        })
        while True:
            message = self.chat.get_next_unprocessed_message('auto_worker')
            if not message:
                break
            self.process_message_as_worker(message)

    def handle_message_created_as_worker(self, message):
        self.process_message_as_worker(Message.load(message['data'], self.redis))

    def process_message_as_worker(self, message):
        print('Message handling: %s' % message.id)
        if random() > 0.85:
            print('Blocked message: %s' % message.id)
            self.chat.block_message('auto_worker', message)
        else:
            print('Approved message: %s' % message.id)
            self.chat.approve_message('auto_worker', message)

    def __del__(self):
        if self.thread:
            self.thread.stop()

    def enter_as_user(self, answers):
        self.session['role'] = constants.USER_ROLE
        login = str(answers['login']).strip()
        me = User.load(self.redis, login)

        if not me:
            me = User(login, 'admin' if login.endswith('admin') else 'user', self.redis)
            me.save()
        if login.endswith('admin'):
            self.thread = self.chat.listen_events({
                '%s:%s' % (constants.EVENT_MESSAGE_CREATED, login): self.handle_message_created,
                '%s:%s' % (constants.EVENT_INCOMING_MESSAGE, login): self.handle_incoming_message,
                '%s:%s' % (constants.EVENT_MESSAGE_APPROVED, login): self.handle_message_approve,
                '%s:%s' % (constants.EVENT_MESSAGE_BLOCKED, login): self.handle_message_block,
                '%s:*' % constants.EVENT_MESSAGE_CREATED: self.handle_else_message_created,
                '%s:*' % constants.EVENT_INCOMING_MESSAGE: self.handle_else_incoming_message,
                '%s:*' % constants.EVENT_MESSAGE_APPROVED: self.handle_else_message_approve,
                '%s:*' % constants.EVENT_MESSAGE_BLOCKED: self.handle_else_message_block,
            })
        else:
            self.thread = self.chat.listen_events({
                '%s:%s' % (constants.EVENT_MESSAGE_CREATED, login): self.handle_message_created,
                '%s:%s' % (constants.EVENT_INCOMING_MESSAGE, login): self.handle_incoming_message,
                '%s:%s' % (constants.EVENT_MESSAGE_APPROVED, login): self.handle_message_approve,
                '%s:%s' % (constants.EVENT_MESSAGE_BLOCKED, login): self.handle_message_block,
            })
        self.session['me'] = me
        UserActionsScene(self.session, self.redis).enter()

    @staticmethod
    def handle_else_message_created(msg):
        print('%s wrote a message' % (msg['channel'].split(':')[1], msg['data']))

    @staticmethod
    def handle_else_incoming_message(msg):
        print('%s has an incoming message %s' % (msg['channel'].split(':')[1], msg['data']))

    @staticmethod
    def handle_else_message_approve(msg):
        print('%s message %s was approved' % (msg['channel'].split(':')[1], msg['data']))

    @staticmethod
    def handle_else_message_block(msg):
        print('%s message %s was blocked' % (msg['channel'].split(':')[1], msg['data']))

    @staticmethod
    def handle_message_created(msg):
        print('Your message %s is ready' % msg['data'])

    @staticmethod
    def handle_incoming_message(msg):
        print('You have a new incoming message: %s' % msg['data'])

    @staticmethod
    def handle_message_approve(msg):
        print('Your message %s was approved' % msg['data'])

    @staticmethod
    def handle_message_block(msg):
        print('Your message %s was blocked' % msg['data'])

    def enter(self):
        while True:
            if self.thread:
                self.thread.stop()
                self.thread = None
            answers = self.ask()
            if 'role' not in answers:
                continue
            if answers['role'] == WORKER:
                self.enter_as_worker()
                break;
            if answers['role'] == USER:
                self.enter_as_user(answers)
            if answers['role'] == EXIT:
                return
