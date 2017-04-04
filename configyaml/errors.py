from __future__ import unicode_literals


class ConfigError(object):
    def __init__(self, title, description=None, line=None, column=None, *args, **kwargs):
        self.title = title
        self.description = description

        # zero based
        self.line = line
        self.column = column
        self.start_line = self.line
        self.start_column = self.column
        self.end_line = kwargs.get('end_line', None)
        self.end_column = kwargs.get('end_column', None)

        self.error_obj = kwargs.get('error_obj', None)

    def __str__(self):
        return self.title

    def as_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'start_line': self.start_line,
            'start_column': self.start_column,
            'end_line': self.end_line,
            'end_column': self.end_column,
        }

    @classmethod
    def create_from_yaml_error(cls, yaml_error):
        if hasattr(yaml_error, 'problem_mark'):
            mark = yaml_error.problem_mark
            return cls(
                line=mark.line,
                column=mark.column,
                title='Basic YAML parsing error',
                description=yaml_error.problem,
                error_obj=yaml_error
            )
        else:
            return cls(
                line=None,
                column=None,
                title='Unknown YAML parsing error',
                description=yaml_error.problem,
                error_obj=yaml_error
            )

    @classmethod
    def create_from_yaml_node(cls, node, *args, **kwargs):
        if 'error_obj' not in kwargs:
            # if no error_obj specified, use node
            kwargs['error_obj'] = node

        if 'line' not in kwargs:
            kwargs['line'] = node.start_mark.line
            kwargs['end_line'] = node.end_mark.line

        if 'column' not in kwargs:
            kwargs['column'] = node.start_mark.column
            kwargs['end_column'] = node.end_mark.column

        return cls(*args, **kwargs)
