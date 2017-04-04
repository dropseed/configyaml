from __future__ import unicode_literals
import pytest

from configyaml.config import NodeList
from configyaml.config import AbstractNode


class DummyFoo(AbstractNode):
    def __init__(self, *args, **kwargs):
        self._type = str
        super(DummyFoo, self).__init__(*args, **kwargs)


class DummyConfigList(NodeList):
    def __init__(self, *args, **kwargs):
        self._list_item_class = DummyFoo
        super(DummyConfigList, self).__init__(*args, **kwargs)


class DummyMinConfigList(NodeList):
    def __init__(self, *args, **kwargs):
        self._min_items_required = 1
        self._list_item_class = DummyFoo
        super(DummyMinConfigList, self).__init__(*args, **kwargs)


def test_list_empty():
    value = []
    config = DummyConfigList(value=value)
    assert config.is_valid()
    assert len(config) == 0

def test_list_none():
    value = None
    config = DummyConfigList(value=value)
    assert len(config) == 0

def test_list_empty_with_minimum():
    value = []
    config = DummyMinConfigList(value=value)
    assert not config.is_valid()
    assert config._errors[0].title == 'Minimum items requirement not met'

def test_list_with_two():
    value = ['a', 'b']
    config = DummyConfigList(value=value)
    assert config.is_valid()
    assert len(config) == 2

def test_list_attr():
    value = ['a', 'b']
    config = DummyConfigList(value=value)
    assert config[0]

def test_assert_on_missing_list_item_class():
    class InvalidConfigList(NodeList):
        pass

    value = ['a', 'b']
    with pytest.raises(AttributeError):
        config = InvalidConfigList(value=value)
