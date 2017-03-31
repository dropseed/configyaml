import pytest

from config_loader.validator import ConfigValidator


def test_invalid_configvalidator_subclass():
    class InvalidConfigValidator(ConfigValidator):
        pass

    with pytest.raises(AttributeError):
        InvalidConfigValidator(config_text="foo: bar")
