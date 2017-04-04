from .base import ConfigBase


class StringNode(ConfigBase):
    """A configuration node that must validate as a string"""
    def __init__(self, *args, **kwargs):
        self._type = str
        super(StringNode, self).__init__(*args, **kwargs)


class IntegerNode(ConfigBase):
    """A configuration node that must validate as an integer"""
    def __init__(self, *args, **kwargs):
        self._type = int
        super(IntegerNode, self).__init__(*args, **kwargs)


class PositiveIntegerNode(IntegerNode):
    """A configuration node that must validate as a positive integer"""
    def _validate_value(self):
        if self._value < 0:
            description = "{value} must be a positive integer".format(value=self._value)
            self._add_error(title="Invalid Value", description=description)
