from __future__ import unicode_literals
import yaml

from .errors import ConfigError


class ConfigLoader(object):
    config_root_class = None

    def __init__(self, config_text, context={}, *args, **kwargs):
        if not self.config_root_class:
            raise AttributeError('config_root_class must defined in subclasses of ConfigLoader')

        self.config_text = config_text
        self.config_dict = None
        self.config_root = None
        self.variable_context = context

        self._errors = []
        self.load()

    def load(self):
        """
        - should not be empty
        - yaml itself should be valid (should we grab more than 1 yaml error at a time?)
        - we should have whitelist of fields the can set at each level, and start
          getting objects out of those, processing grammar if necessary, validating other settings
          errors coming all the way back up
        """
        if not isinstance(self.config_text, str):
            self.config_text = self.config_text.decode('utf-8')

        if not self.config_text.strip():
            self._errors.append(ConfigError(title='YAML is empty', description='Your configuration file appears to be empty.'))
            return

        # simple way to check that yaml itself is valid
        try:
            self.config_dict = yaml.safe_load(self.config_text)
        except yaml.YAMLError as e:
            error = ConfigError.create_from_yaml_error(e)
            self._errors.append(error)
            # could have more than 1 line, keep giong

        if self.config_dict:
            # we have valid yaml with data, so start checking the components
            node_tree = yaml.compose(self.config_text)
            # give it the parsed settings, and the node info
            self.config_root = self.config_root_class(value=self.config_dict, value_node=node_tree, context=self.variable_context)

    @property
    def errors(self):
        if self.config_root:
            return self._errors + self.config_root._get_all_errors()

        return self._errors

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

    def as_text(self):
        if self.is_valid():
            return self.config_text

        else:
            output = []
            errored_lines = set([x.line for x in self.errors])

            for index, line in enumerate(self.config_text.splitlines()):
                output.append(line)
                if index in errored_lines:
                    errors_on_line = [x for x in self.errors if x.line == index]
                    # If there is more than one error on a line, try to group them by title and place in a
                    # single comment block
                    if len(errors_on_line) > 1:
                        error_str = """# {line}\n# ^\n# --------\n""".format(line=line)
                        unique_titles = set([x.title for x in errors_on_line])

                        for t in sorted(unique_titles):
                            error_str += """# {title}\n""".format(title=t)
                            for d in sorted([x.description for x in errors_on_line if x.title == t]):
                                error_str += """# - {description}\n""".format(description=d)

                        error_str += """# --------"""
                    else:
                        e = errors_on_line[0]
                        num_markers = 1 if not e.end_column else e.end_column - e.start_column
                        markers = '^' * num_markers
                        error_str = """\
# {line}
# {markers}
# --------
# {title}
# - {description}
# --------""".format(           line=line,
                            markers=markers.rjust(e.start_column + 1),
                            title=e.title,
                            description=e.description,
                        )
                    output.append(error_str)

            text = '\n'.join([str(x) for x in output])
            return text
