from configyaml.config import PositiveIntegerNode, StringNode, WildcardDictNode, BoolNode, RegexNode
from configyaml.loader import ConfigLoader


class DummyPosIntLoader(ConfigLoader):
    config_root_class = PositiveIntegerNode


def test_wildcard_dict_invalid_key():
    value = {'_bad': 'key'}
    c = WildcardDictNode(value=value)
    assert not c.is_valid()
    assert c._errors[0].title == 'Invalid field name'
    assert c._errors[0].description == 'Cannot start field name with a "_"'

    value = {'*': 'key'}
    c = WildcardDictNode(value=value)
    assert not c.is_valid()
    assert c._errors[0].title == 'Invalid field name'
    assert c._errors[0].description == 'Field name cannot be "*"'


def test_pos_int_invalid_validation():
    value = '-1'
    loader = DummyPosIntLoader(value)
    assert not loader.is_valid()
    assert loader.errors[0].title == "Invalid Value"


def test_pos_int_valid_validation():
    value = '1'
    loader = DummyPosIntLoader(value)
    assert loader.is_valid()


def test_pos_int_zero_validation():
    value = '0'
    loader = DummyPosIntLoader(value)
    assert loader.is_valid()


def test_str_valid():
    value = 'a simple string'
    loader = StringNode(value)
    assert loader.is_valid()


def test_str_invalid():
    value = 99
    loader = StringNode(value)
    assert not loader.is_valid()


# BoolNode tests
def test_bool_valid():
    value = True
    node = BoolNode(value=value)
    assert node.is_valid()

    value = False
    node = BoolNode(value=value)
    assert node.is_valid()


def test_bool_invalid():
    value = 'True'
    node = BoolNode(value=value)
    assert not node.is_valid()

    value = 1
    node = BoolNode(value=value)
    assert not node.is_valid()


# RegexNode tests
def test_regex_valid():
    value = '.*'
    node = RegexNode(value=value)
    assert node.is_valid()
    assert node.regex != None


def test_regex_invalid():
    value = '['
    node = RegexNode(value=value)
    assert not node.is_valid()
    assert node._errors[0].title == 'Invalid regex'
    assert node._errors[0].description in ('unexpected end of regular expression', 'unterminated character set at position 0')
    assert node.regex == None
