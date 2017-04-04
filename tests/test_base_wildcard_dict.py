from __future__ import unicode_literals

from configyaml.config import ConfigBaseWildcardDict


def test_invalid_key():
    value = {'_bad': 'key'}
    c = ConfigBaseWildcardDict(value=value)
    assert not c.is_valid()
    assert c._errors[0].title == 'Invalid field name'
    assert c._errors[0].description == 'Cannot start field name with a "_"'

    value = {'*': 'key'}
    c = ConfigBaseWildcardDict(value=value)
    assert not c.is_valid()
    assert c._errors[0].title == 'Invalid field name'
    assert c._errors[0].description == 'Field name cannot be "*"'
