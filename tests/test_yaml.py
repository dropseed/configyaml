from __future__ import unicode_literals
import sys

from config_loader.config import ConfigBase
from config_loader.config import ConfigBaseDict
from config_loader.config import ConfigBaseList
from config_loader.loader import ConfigLoader
from config_loader.config import ConfigBaseWildcardDict


class DummyConfig(ConfigBaseWildcardDict):
    def __init__(self, *args, **kwargs):
        self._dict_fields = {
            '*': {
                'class': self.__class__,
            },
        }
        super(DummyConfig, self).__init__(*args, **kwargs)


class DummyLoader(ConfigLoader):
    config_root_class = DummyConfig


def test_valid_yaml():
    text = """
string_var: stringy
int_var: 8
float_var: 4.5
bool_var: yes
bool_var2: True
dict_var:
  subdict_var: true
list_var:
- a
- false
    """

    # other things you can do in yaml? http://pyyaml.org/wiki/PyYAMLDocumentation#Tokens

    config = DummyLoader(text)

    assert config['string_var'] == 'stringy'
    assert config['int_var'] == 8
    assert config['float_var'] == 4.5
    assert config['bool_var'] == True
    assert config['bool_var2'] == True
    assert config['dict_var'] == {'subdict_var': True}
    assert config['list_var'] == ['a', False]


def test_invalid_line():
    text = """line_a: True
line_b: !2
line_c: 8"""

    config = DummyLoader(text)

    assert not config.is_valid()
    assert len(config.errors) == 1

    error = config.errors[0]
    assert error.title == 'Basic YAML parsing error'
    assert error.description == "could not determine a constructor for the tag '!2'"
    assert error.line == 1  # 2
    assert error.column == 8  # 9

    assert config.as_text() == """line_a: True
line_b: !2
# line_b: !2
#         ^
# --------
# Basic YAML parsing error
# - could not determine a constructor for the tag '!2'
# --------
line_c: 8"""

    # We want to make sure we're getting unicode back
    if sys.version_info.major < 3:
        assert isinstance(config.as_text(), unicode)
    else:
        assert isinstance(config.as_text(), str)

    assert config.as_dict() == {'config': None,
                                'config_text': 'line_a: True\nline_b: !2\nline_c: 8',
                                'errors': [{'description': "could not determine a constructor for the tag '!2'",
                                        'end_column': None,
                                        'end_line': None,
                                        'start_column': 8,
                                        'start_line': 1,
                                        'title': 'Basic YAML parsing error'}],
                                }

def test_empty_yaml():
    text = """

    """
    config = DummyLoader(text)

    assert not config.is_valid()
    assert len(config.errors) == 1

    error = config.errors[0]
    assert error.title == 'YAML is empty'
    assert error.description == "Your configuration file appears to be empty."
    assert not error.line
    assert not error.column


# can you use mutiple docs? http://pyyaml.org/wiki/PyYAMLDocumentation#LoadingYAML


class StringType(ConfigBase):
    def __init__(self, *args, **kwargs):
        self._type = str
        super(StringType, self).__init__(*args, **kwargs)


class ProjectDict(ConfigBaseDict):
    def __init__(self, *args, **kwargs):
        self._dict_fields = {
            'github': {
                'class': StringType,
                'required': True,
            },
        }
        super(ProjectDict, self).__init__(*args, **kwargs)


class ProjectList(ConfigBaseList):
    def __init__(self, *args, **kwargs):
        self._list_items_class = ProjectDict
        self._min_items_required = 1
        super(ProjectList, self).__init__(*args, **kwargs)


class BaseConfig(ConfigBaseDict):
    def __init__(self, *args, **kwargs):
        self._dict_fields = {
            'projects': {
                'class': ProjectList,
                'required': True,
            },
            'notifications': {
                'class': ProjectList,
                'required': True,
            },
        }
        super(BaseConfig, self).__init__(*args, **kwargs)


class ProjectLoader(ConfigLoader):
    config_root_class = BaseConfig


def test_multiple_invalid_lines():
    text = """\
deadbeef: deadbeef
alist:
    - one
    - two
    - three"""

    config = ProjectLoader(text)
    assert not config.is_valid()

    expected_error = """\
deadbeef: deadbeef
# deadbeef: deadbeef
# ^
# --------
# Invalid key
# - Available fields are: notifications, projects
# Required field is missing
# - notifications is a required field
# - projects is a required field
# --------
alist:
# alist:
# ^^^^^
# --------
# Invalid key
# - Available fields are: notifications, projects
# --------
    - one
    - two
    - three"""
    assert expected_error == config.as_text()
