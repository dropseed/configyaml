from __future__ import unicode_literals

import pytest

from configyaml.config import ListNode
from configyaml.config import AbstractNode


class DummyFoo(AbstractNode):
    def __init__(self, *args, **kwargs):
        self._type = str
        super(DummyFoo, self).__init__(*args, **kwargs)


class DummyConfigListNode(ListNode):
    def __init__(self, *args, **kwargs):
        self._list_item_class = DummyFoo
        super(DummyConfigListNode, self).__init__(*args, **kwargs)


class DummyMinConfigListNode(ListNode):
    def __init__(self, *args, **kwargs):
        self._min_items_required = 1
        self._list_item_class = DummyFoo
        super(DummyMinConfigListNode, self).__init__(*args, **kwargs)


def test_list_empty():
    value = []
    config = DummyConfigListNode(value=value)
    assert config.is_valid()
    assert len(config) == 0

def test_list_none():
    value = None
    config = DummyConfigListNode(value=value)
    assert len(config) == 0

def test_list_empty_with_minimum():
    value = []
    config = DummyMinConfigListNode(value=value)
    assert not config.is_valid()
    assert config._errors[0].title == 'Minimum items requirement not met'

def test_list_with_two():
    value = ['a', 'b']
    config = DummyConfigListNode(value=value)
    assert config.is_valid()
    assert len(config) == 2

def test_list_attr():
    value = ['a', 'b']
    config = DummyConfigListNode(value=value)
    assert config[0]

def test_assert_on_missing_list_item_class():
    class InvalidConfigListNode(ListNode):
        pass

    value = ['a', 'b']
    with pytest.raises(AttributeError):
        config = InvalidConfigListNode(value=value)
