import re

from .base import AbstractNode
from .dict import DictNode


class WildcardDictNode(DictNode):
    """A dictionary node where nearly any key is valid

       The only invalid keys are:
       - an actual asterisk '*'
       - a key that begins with '_'
       """
    def _validate_value(self):
        for key, value in self._value.items():
            # where key name doesn't matter (ex. groups)
            key_valid, explanation = self._key_name_is_valid(key)
            if key_valid:
                field_class = self._dict_fields['*']['class']
                field = field_class(value=value, value_node=self._find_node_for_key_value(key),
                                    context=self._context, key=key, parent=self)

                # don't set __dict__ if they can use any key
                self._children[key] = field
            else:
                self._add_error(
                    node=self._find_node_for_key(key),
                    title='Invalid field name',
                    description=explanation
                )

    def _as_dict(self):
        d = {}
        for group_name in self._children.keys():
            d[group_name] = self[group_name]._as_dict()

        if self._errors:
            d['errors'] = [x.as_dict() for x in self._errors]

        d.update(self._as_dict_to_inject())

        return d

    def _key_name_is_valid(self, key):
        if key == '*':
            return False, 'Field name cannot be "*"'

        if key.startswith('_'):
            return False, 'Cannot start field name with a "_"'

        return True, 'Valid'


class BoolNode(AbstractNode):
    """A node that must validate as a bool"""
    def __init__(self, *args, **kwargs):
        self._type = bool
        super(BoolNode, self).__init__(*args, **kwargs)


class StringNode(AbstractNode):
    """A node that must validate as a string"""
    def __init__(self, *args, **kwargs):
        self._type = str
        super(StringNode, self).__init__(*args, **kwargs)


class RegexNode(StringNode):
    """A node that must validate as a regular expression"""
    def __init__(self, *args, **kwargs):
        self.regex = None
        super(RegexNode, self).__init__(*args, **kwargs)

    def _validate_value(self):
        try:
            self.regex = re.compile(self._value)
        except re.error as e:
            self._add_error(title='Invalid regex', description=str(e))


class IntegerNode(AbstractNode):
    """A node that must validate as an integer"""
    def __init__(self, *args, **kwargs):
        self._type = int
        super(IntegerNode, self).__init__(*args, **kwargs)


class PositiveIntegerNode(IntegerNode):
    """A node that must validate as a positive integer"""
    def _validate_value(self):
        if self._value < 0:
            description = "{value} must be a positive integer".format(value=self._value)
            self._add_error(title="Invalid Value", description=description)


class TypelessNode(AbstractNode):
    """A node that does not have to validate as any specific type"""
    def _validate_type(self):
        pass
