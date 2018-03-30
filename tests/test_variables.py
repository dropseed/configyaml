import pytest

from configyaml.config.nodes import StringNode, BoolNode
from .test_loader import DummyLoader, DummyComplexLoader


def test_variable_match():
    n = StringNode(value='$var', variables={'var': 'testing'})
    assert n.is_valid()
    assert n._value == 'testing'

    assert n._as_dict() == {'value': 'testing'}
    assert n._as_dict(redact=True) == {'value': '[REDACTED]', 'redacted': True}


def test_variable_no_match():
    n = StringNode(value='$$var', variables={'var': 'testing'})
    assert not n.is_valid()
    assert n._value == '$$var'
    assert n._errors[0].title == 'Variable not found'

    assert n._as_dict() == {
        'errors': [
            {
                'description': "'$var' was not found in ['var']",
                'end_column': None,
                'end_line': None,
                'start_column': None,
                'start_line': None,
                'title': 'Variable not found',
            }
        ],
        'value': '$$var',
    }

    assert n._as_dict(redact=True) == {
        'errors': [
            {
                'description': "'$var' was not found in ['var']",
                'end_column': None,
                'end_line': None,
                'start_column': None,
                'start_line': None,
                'title': 'Variable not found',
            }
        ],
        'value': '$$var',
    }


def test_variable_escaped():
    n = StringNode(value='\$var', variables={'var': 'testing'})
    assert n.is_valid()
    assert n._value == '$var'

    assert n._as_dict() == {'value': '$var'}
    assert n._as_dict(redact=True) == {'value': '$var'}


def test_variable_case_sensitive():
    n = StringNode(value='$VAR', variables={'var': 'testing'})
    assert not n.is_valid()
    assert n._value == '$VAR'
    assert n._errors[0].title == 'Variable not found'

    assert n._as_dict() == {
        'errors': [
            {
                'description': "'VAR' was not found in ['var']",
                'end_column': None,
                'end_line': None,
                'start_column': None,
                'start_line': None,
                'title': 'Variable not found',
            }
        ],
        'value': '$VAR',
    }

    assert n._as_dict(redact=True) == {
        'errors': [
            {
                'description': "'VAR' was not found in ['var']",
                'end_column': None,
                'end_line': None,
                'start_column': None,
                'start_line': None,
                'title': 'Variable not found',
            }
        ],
        'value': '$VAR',
    }

    n = StringNode(value='$vaR', variables={'vaR': 'testing'})
    assert n.is_valid()
    assert n._value == 'testing'

    assert n._as_dict() == {'value': 'testing'}
    assert n._as_dict(redact=True) == {'value': '[REDACTED]', 'redacted': True}


def test_no_variables():
    n = StringNode(value='$var')
    assert not n.is_valid()
    assert n._value == '$var'

    assert n._as_dict() == {
        'errors': [
            {
                'description': "'var' was not found in []",
                'end_column': None,
                'end_line': None,
                'start_column': None,
                'start_line': None,
                'title': 'Variable not found',
            }
        ],
        'value': '$var',
    }

    assert n._as_dict(redact=True) == {
        'errors': [
            {
                'description': "'var' was not found in []",
                'end_column': None,
                'end_line': None,
                'start_column': None,
                'start_line': None,
                'title': 'Variable not found',
            }
        ],
        'value': '$var',
    }


def test_variables_type_error():
    with pytest.raises(TypeError):
        StringNode(value='$var', variables='testing')


def test_bool_node_variable():
    n = BoolNode(value='$test', variables={'test': True})
    assert n.is_valid()
    assert n._value == True

    assert n._as_dict() == {'value': True}
    assert n._as_dict(redact=True) == {'value': '[REDACTED]', 'redacted': True}


def test_bool_node_variable_bad_type():
    n = BoolNode(value='$test', variables={'test': 'ok'})
    assert not n.is_valid()
    assert n._value == 'ok'

    assert n._as_dict() == {
        'errors': [
            {
                'description': "boolnode must be a bool",
                'end_column': None,
                'end_line': None,
                'start_column': None,
                'start_line': None,
                'title': 'boolnode has an invalid type',
            }
        ],
        'value': 'ok',
    }

    assert n._as_dict(redact=True) == {
        'errors': [
            {
                'description': "boolnode must be a bool",
                'end_column': None,
                'end_line': None,
                'start_column': None,
                'start_line': None,
                'title': 'boolnode has an invalid type',
            }
        ],
        'value': '[REDACTED]',
        'redacted': True,
    }


def test_loader_with_variables():
    value = "{ 'foo': '$bar'}"
    loader = DummyLoader(value, variables={'bar': 'testing'})
    assert loader.is_valid()

    assert loader.as_text() == "{ 'foo': '$bar'}"
    assert loader.as_dict() == {
        'config': {'foo': {'value': 'testing'}}, 'config_text': "{ 'foo': '$bar'}"
    }
    assert loader.as_dict(redact=True) == {
        'config': {'foo': {'redacted': True, 'value': '[REDACTED]'}},
        'config_text': "{ 'foo': '$bar'}",
    }


def test_loader_with_missing_variable():
    value = "{ 'foo': '$bar'}"
    loader = DummyLoader(value, variables={'boo': 'testing'})
    assert not loader.is_valid()
    assert loader.errors[0].title == 'Variable not found'

    assert loader.as_text() == """{ 'foo': '$bar'}
# { 'foo': '$bar'}
#     ^^^^^^
# --------
# Variable not found
# - 'bar' was not found in ['boo']
# --------"""

    assert loader.as_dict() == {
        'config': {
            'foo': {
                'errors': [
                    {
                        'description': "'bar' was not found in ['boo']",
                        'end_column': 15,
                        'end_line': 0,
                        'start_column': 9,
                        'start_line': 0,
                        'title': 'Variable not found',
                    }
                ],
                'value': '$bar',
            }
        },
        'config_text': "{ 'foo': '$bar'}",
        'errors': [
            {
                'description': "'bar' was not found in ['boo']",
                'end_column': 15,
                'end_line': 0,
                'start_column': 9,
                'start_line': 0,
                'title': 'Variable not found',
            }
        ],
    }
    assert loader.as_dict(redact=True) == {
        'config': {
            'foo': {
                'errors': [
                    {
                        'description': "'bar' was not found in ['boo']",
                        'end_column': 15,
                        'end_line': 0,
                        'start_column': 9,
                        'start_line': 0,
                        'title': 'Variable not found',
                    }
                ],
                'value': '$bar',
            }
        },
        'config_text': "{ 'foo': '$bar'}",
        'errors': [
            {
                'description': "'bar' was not found in ['boo']",
                'end_column': 15,
                'end_line': 0,
                'start_column': 9,
                'start_line': 0,
                'title': 'Variable not found',
            }
        ],
    }


def test_loader_with_nested_variables():
    value = 'foo: $list_var\nbar: yay'
    variables = {'list_var': ['one', 'two', '$three_var'], 'three_var': 'THREE!'}
    loader = DummyComplexLoader(value, variables=variables)
    assert loader.is_valid()

    assert loader.as_text() == 'foo: $list_var\nbar: yay'
    assert loader.as_dict() == {
        'config': {
            'bar': {'value': 'yay'},
            'foo': {'items': [{'value': 'one'}, {'value': 'two'}, {'value': 'THREE!'}]},
        },
        'config_text': 'foo: $list_var\nbar: yay',
    }
    assert loader.as_dict(redact=True) == {
        'config': {
            'bar': {'value': 'yay'}, 'foo': {'redacted': True, 'value': '[REDACTED]'}
        },
        'config_text': 'foo: $list_var\nbar: yay',
    }


def test_loader_with_nested_list_variable_missing():
    value = 'foo: $list_var\nbar: yay'
    variables = {
        'list_var': ['one', 'two', '$three_var'], 'threeve': 'THREE!'  # one key
    }
    loader = DummyComplexLoader(value, variables=variables)
    assert not loader.is_valid()

    text = loader.as_text()
    assert text == """foo: $list_var
# foo: $list_var
# ^^^^^^^^^
# --------
# Variable not found
# - 'three_var' was not found in ['list_var', 'threeve']
# --------
bar: yay"""

    # the variable content should not be visible, only the variable keys
    assert '$three_var' not in text

    assert loader.as_dict() == {
        'config': {
            'bar': {'value': 'yay'},
            'foo': {
                'items': [
                    {'value': 'one'},
                    {'value': 'two'},
                    {
                        'errors': [
                            {
                                'description': "'three_var' was not "
                                'found in '
                                "['list_var', "
                                "'threeve']",
                                'end_column': 14,
                                'end_line': 0,
                                'start_column': 5,
                                'start_line': 0,
                                'title': 'Variable not found',
                            }
                        ],
                        'value': '$three_var',
                    },
                ]
            },
        },
        'config_text': 'foo: $list_var\nbar: yay',
        'errors': [
            {
                'description': "'three_var' was not found in ['list_var', "
                "'threeve']",
                'end_column': 14,
                'end_line': 0,
                'start_column': 5,
                'start_line': 0,
                'title': 'Variable not found',
            }
        ],
    }
    assert loader.as_dict(redact=True) == {
        'config': {
            'bar': {'value': 'yay'}, 'foo': {'redacted': True, 'value': '[REDACTED]'}
        },
        'config_text': 'foo: $list_var\nbar: yay',
        'errors': [
            {
                'description': "'three_var' was not found in ['list_var', "
                "'threeve']",
                'end_column': 14,
                'end_line': 0,
                'start_column': 5,
                'start_line': 0,
                'title': 'Variable not found',
            }
        ],
    }
