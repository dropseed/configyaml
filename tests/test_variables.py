import pytest

from configyaml.config.nodes import StringNode, BoolNode
from .test_loader import DummyLoader


def test_variable_match():
    n = StringNode(value='$var', variables={'var': 'testing'})
    assert n.is_valid()
    assert n._value == 'testing'


def test_variable_no_match():
    n = StringNode(value='$$var', variables={'var': 'testing'})
    assert not n.is_valid()
    assert n._value == '$$var'
    assert n._errors[0].title == 'Variable not found'


def test_variable_escaped():
    n = StringNode(value='\$var', variables={'var': 'testing'})
    assert n.is_valid()
    assert n._value == '$var'


def test_variable_case_sensitive():
    n = StringNode(value='$VAR', variables={'var': 'testing'})
    assert not n.is_valid()
    assert n._value == '$VAR'
    assert n._errors[0].title == 'Variable not found'

    n = StringNode(value='$vaR', variables={'vaR': 'testing'})
    assert n.is_valid()
    assert n._value == 'testing'


def test_no_variables():
    n = StringNode(value='$var')
    assert n.is_valid()
    assert n._value == '$var'


def test_variables_type_error():
    with pytest.raises(TypeError):
        StringNode(value='$var', variables='testing')


def test_bool_node_variable():
    n = BoolNode(value='$test', variables={'test': True})
    assert n.is_valid()
    assert n._value == True


def test_bool_node_variable_bad_type():
    n = BoolNode(value='$test', variables={'test': 'ok'})
    assert not n.is_valid()
    assert n._value == 'ok'


def test_loader_with_variables():
    value = "{ 'foo': '$bar'}"
    loader = DummyLoader(value, variables={'bar': 'testing'})
    assert loader.is_valid()
    assert loader.as_dict()['config'] == {'foo': {'value': 'testing'}}


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
