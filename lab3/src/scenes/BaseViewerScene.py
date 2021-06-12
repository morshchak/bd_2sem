from .BaseScene import BaseScene
import math
import abc

BACK = 'Back'
NEXT = 'Next'
EXIT = 'Return'
ITEMS_PER_PAGE = 10


class BaseViewerScene(BaseScene):
    def __init__(self, items_per_page=ITEMS_PER_PAGE):
        super().__init__([
            {
                'type': 'list',
                'name': 'action',
                'message': 'Navigation',
                'choices': [NEXT, BACK, EXIT]
            }
        ])
        self.items_per_page = items_per_page
        self.cursor = 0

    def load(self):
        items = self.fetch(self.cursor, self.cursor + ITEMS_PER_PAGE)
        if not len(items):
            return []
        else:
            return items

    @abc.abstractmethod
    def fetch(self, start, end):
        pass

    @abc.abstractmethod
    def items_count(self):
        pass

    def next_page(self):
        self.cursor += ITEMS_PER_PAGE
        if self.cursor > self.items_count():
            self.cursor = 0

    def prev_page(self):
        self.cursor -= ITEMS_PER_PAGE
        if self.cursor < 0:
            self.cursor = 0

    def enter(self):
        while True:
            print('Page №%i' % math.ceil(self.cursor // ITEMS_PER_PAGE))
            print('Total %i' % self.items_count())
            print('\n'.join(self.load()))
            answers = self.ask()
            action = answers['action']
            if action == NEXT:
                self.next_page()
            elif action == BACK:
                self.prev_page()
            else:
                return
