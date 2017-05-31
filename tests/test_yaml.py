from __future__ import unicode_literals
import sys

from configyaml.config import AbstractNode
from configyaml.config import DictNode
from configyaml.config import ListNode
from configyaml.loader import ConfigLoader
from configyaml.config import WildcardDictNode
from configyaml.config import TypelessNode


class DummyConfig(WildcardDictNode):
    def __init__(self, *args, **kwargs):
        self._dict_fields = {
            '*': {
                'class': TypelessNode,
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

    assert config.is_valid()

    assert config['string_var'] == 'stringy'
    assert config['int_var'] == 8
    assert config['float_var'] == 4.5
    assert config['bool_var'] == True
    assert config['bool_var2'] == True
    assert config['dict_var'] == {'subdict_var': True}
    assert config['list_var'] == ['a', False]


def test_invalid_python_type():
    text = """
  string_var: stringy
  int_var: 8
  float_var: 4.5
  python_str_var: !!python/str "test"
    """

    config = DummyLoader(text)

    assert not config.is_valid()
    assert config.errors[0].description == "could not determine a constructor for the tag 'tag:yaml.org,2002:python/str'"


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

def test_bytes_in_unicode_out():
    """Test to make sure that even if we put in bytes that we get out uniform utf8 text, original lines as
       well as error lines.  We've had errors where the output in Python3 has the original lines prefixed
       with 'b' and we want to make sure that doesn't happen again."""
    text = """line_a: True
line_b: !2
line_c: 8"""

    config = DummyLoader(text.encode('utf-8'))

    assert not config.is_valid()

    # We want to make sure we're getting unicode back
    if sys.version_info.major < 3:
        assert isinstance(config.as_text(), unicode)
    else:
        assert isinstance(config.as_text(), str)

    assert config.as_text() == """line_a: True
line_b: !2
# line_b: !2
#         ^
# --------
# Basic YAML parsing error
# - could not determine a constructor for the tag '!2'
# --------
line_c: 8"""




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


class StringType(AbstractNode):
    def __init__(self, *args, **kwargs):
        self._type = str
        super(StringType, self).__init__(*args, **kwargs)


class ProjectDictNode(DictNode):
    def __init__(self, *args, **kwargs):
        self._dict_fields = {
            'github': {
                'class': StringType,
                'required': True,
            },
        }
        super(ProjectDictNode, self).__init__(*args, **kwargs)


class ProjectListNode(ListNode):
    def __init__(self, *args, **kwargs):
        self._list_items_class = ProjectDictNode
        self._min_items_required = 1
        super(ProjectListNode, self).__init__(*args, **kwargs)


class BaseConfig(DictNode):
    def __init__(self, *args, **kwargs):
        self._dict_fields = {
            'projects': {
                'class': ProjectListNode,
                'required': True,
            },
            'notifications': {
                'class': ProjectListNode,
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
