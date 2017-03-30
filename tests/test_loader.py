from __future__ import unicode_literals

import pytest

from config_loader.config import ConfigBaseList
from config_loader.loader import ConfigLoader
from config_loader.config import ConfigBaseDict
from config_loader.config import ConfigBase


class DummyFoo(ConfigBase):
    def __init__(self, *args, **kwargs):
        self._type = str
        super(DummyFoo, self).__init__(*args, **kwargs)


class DummyConfig(ConfigBaseDict):
    def __init__(self, *args, **kwargs):
        self._dict_fields = {
            'foo': {
                'class': DummyFoo,
            }
        }
        super(DummyConfig, self).__init__(*args, **kwargs)


class DummyLoader(ConfigLoader):
    config_root_class = DummyConfig


class DummyComplexConfig(ConfigBaseDict):
    def __init__(self, *args, **kwargs):
        self._dict_fields = {
            'foo': {
                'class': DummyMinConfigList,
            },
            'bar': {
                'class': DummyFoo,
            }
        }
        super(DummyComplexConfig, self).__init__(*args, **kwargs)


class DummyMinConfigList(ConfigBaseList):
    def __init__(self, *args, **kwargs):
        self._min_items_required = 1
        self._list_item_class = DummyFoo
        super(DummyMinConfigList, self).__init__(*args, **kwargs)


class DummyComplexLoader(ConfigLoader):
    config_root_class = DummyComplexConfig


def test_dict_error_propogation():
    value = """foo: ['list']"""
    loader = DummyLoader(value)
    assert not loader.is_valid()
    assert len(loader.errors) == 1

    assert len(loader.config_root._errors) == 0
    assert len(loader.config_root._get_descendants_errors()) == 1
    assert len(loader.config_root._get_all_errors()) == 1

    assert len(loader.config_root.foo._errors) == 1
    assert len(loader.config_root.foo._get_descendants_errors()) == 0
    assert len(loader.config_root.foo._get_all_errors()) == 1


def test_as_dict():
    value = "{ 'foo': 'bar'}"
    loader = DummyLoader(value)
    assert loader.is_valid()
    assert loader.as_dict()['config'] == {'foo': {'value':'bar'}}

def test_as_dict_with_lists():
    value = "{ 'foo': ['x', 'y'], 'bar': 'deadbeef'}"
    loader = DummyComplexLoader(value)
    assert loader.is_valid()
    assert loader.as_dict()['config'] == {'foo': {'items': [{'value': 'x'}, {'value': 'y'}]}, 'bar': {'value': 'deadbeef'}}
# def test_list_error_propogation():


def test_asserts_on_invalid_subclass():
    class InvalidLoader(ConfigLoader):
        pass

    value = ['a', 'b']
    with pytest.raises(AttributeError):
        InvalidLoader(value)
