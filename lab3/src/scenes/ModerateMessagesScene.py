from .BaseScene import BaseScene
from src import constants
from pprint import pprint

APPROVE = 'approve'
BLOCK = 'spam'
ITEMS_PER_PAGE = 10
LOAD_NEW_PROMPT = [{
    'type': 'confirm',
    'name': 'continue',
    'message': 'Load new?',
}]


class ModerateMessagesScene(BaseScene):
    def __init__(self, session, redis, driver):
        super().__init__([
            {
                'type': 'list',
                'name': 'action',
                'message': 'Choose action:',
                'choices': [APPROVE, BLOCK]
            },
            {
                'type': 'confirm',
                'name': 'continue',
                'message': 'Continue?',
            }
        ])
        self.chat = session['chat']
        self.session = session
        self.redis = redis
        self.message = None
        self.driver = driver

    def load_next_message(self):
        self.message = self.chat.get_next_unprocessed_message(self.session['me'].login)

    def approve_message(self):
        self.chat.approve_message(self.session['me'].login, self.message)

    def block_message(self):
        self.chat.block_message(self.session['me'].login, self.message)

    def enter(self):
        while True:
            self.load_next_message()
            pprint(self.message.to_dict() if self.message else "No new messages")
            answers = self.ask(None if self.message else LOAD_NEW_PROMPT)
            if 'action' not in answers:
                return
            action = answers['action'] if 'action' in answers else None
            if action == APPROVE:
                self.approve_message()
            elif action == BLOCK:
                self.block_message()
            if not answers['continue']:
                break
