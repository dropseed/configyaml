import yaml

from .errors import ConfigError


class ConfigLoader(object):
    config_root_class = None

    def __init__(self, config_text, context={}, *args, **kwargs):
        assert self.config_root_class is not None

        self.config_text = config_text
        self.config_dict = None
        self.config_root = None
        self.variable_context = context

        self.errors = []
        self.load()

    def load(self):
        """
        - should not be empty
        - yaml itself should be valid (should we grab more than 1 yaml error at a time?)
        - we should have whitelist of fields the can set at each level, and start
          getting objects out of those, processing grammar if necessary, validating other settings
          errors coming all the way back up
        """

        if not self.config_text.strip():
            self.errors.append(ConfigError(title='YAML is empty', description='Your configuration file appears to be empty.'))
            return

        # simple way to check that yaml itself is valid
        try:
            self.config_dict = yaml.load(self.config_text)
        except yaml.YAMLError as e:
            error = ConfigError.create_from_yaml_error(e)
            self.errors.append(error)
            # could have more than 1 line, keep giong

        if self.config_dict:
            # we have valid yaml with data, so start checking the components
            node_tree = yaml.compose(self.config_text)
            # give it the parsed settings, and the node info
            self.config_root = self.config_root_class(value=self.config_dict, value_node=node_tree, context=self.variable_context)
            self.errors = self.errors + self.config_root._get_all_errors()

    def is_valid(self):
        return not self.errors

    def __getitem__(self, key):
        # just pass off as dict right now
        return self.config_dict[key]

    def as_dict(self):
        d = {
            'config_text': self.config_text,
            'config': self.config_root._as_dict() if self.config_root else None,
        }
        if self.errors:
            d['errors'] = [x.as_dict() for x in self.errors]
        return d

    def as_text(self, simple=False):
        if self.is_valid():
            return self.config_text

        else:
            output = []
            errored_lines = set([x.line for x in self.errors])

            for index, line in enumerate(self.config_text.splitlines()):
                if simple:
                    if index in errored_lines:
                        output.append('{}  # FIXME <url>'.format(line))
                    else:
                        output.append(line)
                else:
                    output.append(line)
                    if index in errored_lines:
                        errors_on_line = [x for x in self.errors if x.line == index]
                        for e in errors_on_line:
                            num_markers = 1 if not e.end_column else e.end_column - e.start_column
                            markers = '^' * num_markers
                            error_str = """{markers}
--------
{title}
- {description}
--------""".format(
                                markers=markers.rjust(e.start_column + 1),
                                title=e.title,
                                description=e.description,
                            )
                            output.append(error_str)

            text = '\n'.join(output)
            return text
