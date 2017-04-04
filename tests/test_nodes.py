from config_loader.config.nodes import PositiveIntegerNode, StringNode
from config_loader.loader import ConfigLoader


class DummyPosIntLoader(ConfigLoader):
    config_root_class = PositiveIntegerNode


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


class StringLoader(ConfigLoader):
    config_root_class = StringNode


def test_str_valid():
    value = 'a simple string'
    loader = StringLoader(value)
    assert loader.is_valid()
