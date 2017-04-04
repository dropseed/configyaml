from .loader import ConfigLoader


class ConfigValidator(object):
    """A stripped down class for performing validation only (uses dummy context)"""
    configyaml_class = ConfigLoader
    context = None

    def __init__(self, config_text):
        if not self.context:
            raise AttributeError('self.context must be defined in subclasses of ConfigValidator')
        self.loader = self.configyaml_class(config_text=config_text, context=self.context)
        self.errors = self.loader.errors

    def is_valid(self):
        return not self.errors

    def as_dict(self):
        return self.loader.as_dict()
