from .loader import ConfigLoader


class ConfigValidator(object):
    """A stripped down class for performing validation only (uses dummy context)"""
    config_loader_class = ConfigLoader

    def __init__(self, config_text):
        assert self.context
        self.loader = self.config_loader_class(config_text=config_text, context=self.context)
        self.errors = self.loader.errors

    def is_valid(self):
        return not self.errors

    def as_dict(self):
        return self.loader.as_dict()
