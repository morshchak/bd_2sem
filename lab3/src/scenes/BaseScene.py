from PyInquirer import prompt


class BaseScene:
    def __init__(self, questions):
        self.questions = questions
        self.clear()

    def clear(self):
        print('\x1bc')

    def ask(self, questions=None, clear=True):
        answers = prompt(questions or self.questions)
        if clear:
            self.clear()
        return answers
