from ..errors import ConfigError


class AbstractNode(object):
    """Configuration Base Class

    All nodes in the configuration inherit from this base class
    to define types of nodes and groups of nodes; it is not intended
    to be used directly, but rather to be subclassed.

    """
    def __init__(self, value, value_node=None, context={}, *args, **kwargs):
        """Initialize a node

        :param value:
        :param value_node:
        :param context:
        :param args:
        :param kwargs:
        """
        self._value = value
        self._value_node = value_node  # yaml node obj
        self._context = context

        # optionally pass in the name that this setting was under
        # especially for wildcards like group name
        self._key = kwargs.get('key', None)
        self._parent = kwargs.get('parent', None)

        self._validate()

        # probably a nicer way to do this by breaking down the steps
        # (creating all objects, setting context, then validating) but turned out to be a mess in 1st try
        if self._context_to_inject():
            self._context.update(self._context_to_inject())
            # then we need to revalidate with that context
            self._validate()

    def is_valid(self):  # type: () -> bool
        """Tests whether this node is valid (but not descendants)

        :rtype: bool
        """
        return not self._errors

    def _key_name(self):  # type: () -> str
        """Return the key referring to this object

        The default value is the lower case version of the class name

        :rtype: str
        """
        if self._key is not None:
            return self._key

        return self.__class__.__name__.lower()

    def __nonzero__(self):  # type: () -> bool
        """Python 2 support for object truth

        :rtype: bool
        """
        return True

    def __bool__(self):  # type: () -> bool
        """Python 3 support for object truth

        :rtype: bool
        """
        return True

    def _path(self):  # type: () -> str
        """Return the dotted path representation of this object

        :rtype: str
        """
        if self._parent:
            return '{}.{}'.format(self._parent._path(), self._key_name())

        return self._key_name()

    def _add_error(self, *args, **kwargs):  # type: () -> None
        """Convenience function to add an error to this object, with line numbers

        :rtype: None
        """
        if kwargs.get('node', None):
            # if node specified and not none
            error = ConfigError.create_from_yaml_node(
                *args,
                **kwargs
            )
        elif self._value_node:
            # default to using the node if we have one
            error = ConfigError.create_from_yaml_node(
                node=self._value_node,
                *args,
                **kwargs
            )
        else:
            # no nodes or error_obj to attach
            error = ConfigError(*args, **kwargs)

        self._errors.append(error)

    def _get_descendants_errors(self):  # type: () -> List(ConfigError)
        """Recursively get errors from descendants

        :rtype: list of :ConfigErrors:"""
        descendants_errors = []
        if hasattr(self, '_children'):
            if isinstance(self._children, (list, tuple)):
                for c in self._children:
                    descendants_errors += c._get_all_errors()
            elif isinstance(self._children, dict):
                for c in self._children.values():
                    descendants_errors += c._get_all_errors()

        return descendants_errors

    def _get_all_errors(self):  # type: () -> List(ConfigError)
        """Collect and return a list of all errors

        Collects all errors from this node and all of its descendants.

        :rtype: list of :ConfigErrors:
        """
        return self._errors + self._get_descendants_errors()

    def _validate(self):  # type: () -> None
        """Run validation, save errors to object in self._errors"""
        # class can specify it's empty obj -- list would have empty of []
        self._errors = []

        self._validate_type()

        if self.is_valid():
            self._validate_value()

    def _validate_type(self):  # type: () -> None
        """Validation to ensure value is the correct type"""
        if not isinstance(self._value, self._type):
            title = '{} has an invalid type'.format(self._key_name())
            description = '{} must be a {}'.format(self._key_name(), self._type.__name__)

            self._add_error(title=title, description=description)

    def _validate_value(self):  # type: () -> None
        """Do custom validation here, only runs if valid up to this point"""
        pass

    def _context_to_inject(self):  # type: () -> dict
        """An optional dictionary of context to be injected into children"""
        return {}

    def _as_dict_to_inject(self):  # type: () -> dict
        """Additional fields to inject into as_dict"""
        return {}

    def _as_dict(self):  # type: () -> dict
        d = {'value': self._value}
        if self._errors:
            d['errors'] = [x.as_dict() for x in self._errors]
        d.update(self._as_dict_to_inject())
        return d
