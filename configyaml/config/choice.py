from .base import AbstractNode


class ChoiceNode(AbstractNode):
    _choices = None

    def __init__(self, *args, **kwargs):
        self._type = str

        if not self._choices:
            # class should specify self._choices = []  # list of choices that the str can be
            raise AttributeError('_choices must be defined in subclasses of ConfigBaseChoices')

        super(ChoiceNode, self).__init__(*args, **kwargs)

    def _validate_value(self):
        if self._value not in self._choices:
            self._add_error(
                title='Invalid choice',
                description='Must be one of {}'.format(', '.join(self._choices)),
            )
