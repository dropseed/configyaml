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


# def test_list_error_propogation():
