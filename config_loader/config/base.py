from ..errors import ConfigError


class ConfigBase(object):
    def __init__(self, value, value_node=None, context={}, *args, **kwargs):
        self._value = value
        self._value_node = value_node
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

    def _as_dict(self):
        raise NotImplementedError

    def is_valid(self):
        return not self._errors

    def _key_name(self):
        # use the class name by default, lowered
        if self._key is not None:
            return self._key

        return self.__class__.__name__.lower()

    def _path(self):
        if self._parent:
            return '{}.{}'.format(self._parent._path(), self._key_name())

        return self._key_name()

    def _add_error(self, *args, **kwargs):
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

    def _validate(self):
        self._objs = self._empty_objs if hasattr(self, '_empty_objs') else None
        self._errors = []

        self._validate_type()

    def _validate_type(self):
        if not isinstance(self._value, self._type):
            title = '{} has an invalid type'.format(self._key_name())
            description = '{} must be a {}'.format(self._key_name(), self._type.__name__)

            self._add_error(title=title, description=description)

    def _context_to_inject(self):
        """An optional dictionary of context to be injected into children"""
        return {}

    def _as_dict_to_inject(self):
        """Additional fields to inject into as_dict"""
        return {}

    def _as_dict(self):
        d = {
            'value': self._value,
            'errors': [x.as_dict() for x in self._errors],
        }
        d.update(self._as_dict_to_inject())
        return d


class ConfigBaseList(ConfigBase):
    def __init__(self, *args, **kwargs):
        self._type = list
        self._empty_objs = []
        super(ConfigBaseList, self).__init__(*args, **kwargs)

    def _validate(self):
        super(ConfigBaseList, self)._validate()

        if not self.is_valid():
            return

        for index, item in enumerate(self._value):
            field_class = self._list_item_class
            field = field_class(value=item, value_node=self._find_node_for_list_index(index), context=self._context, parent=self, key=index)
            self._errors = self._errors + field._errors

            self._objs.append(field)

    def _find_node_for_list_index(self, index):
        if not self._value_node:
            return None

        return self._value_node.value[index]

    def __getitem__(self, key):
        return self._objs[key]

    def __len__(self):
        return len(self._objs)

    def _as_dict(self):
        d = {
            'items': [x._as_dict() for x in self._objs],
            'errors': [x.as_dict() for x in self._errors],
            'valid': self.is_valid(),
        }
        d.update(self._as_dict_to_inject())
        return d


class ConfigBaseDict(ConfigBase):
    def __init__(self, *args, **kwargs):
        self._type = dict
        self._empty_objs = {}
        super(ConfigBaseDict, self).__init__(*args, **kwargs)

    def _validate(self):
        super(ConfigBaseDict, self)._validate()

        if not self.is_valid():
            return

        keys = self._value.keys()
        available_keys = self._dict_fields.keys()  # in python3 doesn't return a true list, dict_keys set-like obj instead

        # TODO could check len(keys) > 0
        # any point in having empty dicts

        def valid_key_name(key):
            if key == '*':
                return False, 'Name cannot be "*"'

            if key.startswith('_'):
                return False, 'Cannot start name with a "_"'

            return True, 'Valid'

        # assign defaults first
        for k in available_keys:
            self.__dict__[k] = self._dict_fields[k]['class'](value={})
            self._objs[k] = self._dict_fields[k]['class'](value={})

        for key in keys:
            is_valid, is_valid_explanation = valid_key_name(key)
            if key in available_keys and is_valid:
                # get class for key
                field_class = self._dict_fields[key]['class']
                field = field_class(value=self._value[key], value_node=self._find_node_for_key_value(key), context=self._context, parent=self)
                self._errors = self._errors + field._errors

                # set self.FIELD_NAME so we can get children directly
                # these will only be keys we specify, so should be safe names
                self.__dict__[key] = field
                self._objs[key] = field

            elif not is_valid:
                self._add_error(
                    node=self._find_node_for_key(key),
                    title='Invalid key name',
                    description=is_valid_explanation,
                )
            else:
                # cannot use key
                self._add_error(
                    node=self._find_node_for_key(key),
                    title='Invalid key',
                    description='Available fields are: {}'.format(available_keys),
                )

    def _find_node_for_key_value(self, key):
        if not self._value_node:
            return None

        for children in self._value_node.value:
            # value would be the second ScalarNode
            if len(children) > 1:
                key_node = children[0]
                if key_node.value == key:
                    return children[1]  # return the following value node

        return None

    def _find_node_for_key(self, key):
        if not self._value_node:
            return None

        for children in self._value_node.value:
            # key would be the first ScalarNode
            key_node = children[0]
            if key_node.value == key:
                return key_node

        return None

    def __getitem__(self, key):
        return self._objs[key]

    def __len__(self):
        return len(self._objs)

    def _as_dict(self):
        d = {}
        for k in self._dict_fields.keys():
            d[k] = self[k]._as_dict()

        d['errors'] = [x.as_dict() for x in self._errors]
        d['valid'] = self.is_valid()
        d.update(self._as_dict_to_inject())

        return d


class ConfigBaseWildcardDict(ConfigBaseDict):
    def _validate(self):
        # TODO still dumb here
        self._objs = {}
        self._errors = []
        self._validate_type()

        if not self.is_valid():
            return

        for key in self._value.keys():
            # where key name doesn't matter (ex. groups)
            field_class = self._dict_fields['*']['class']
            field = field_class(value=self._value[key], value_node=self._find_node_for_key_value(key), context=self._context, key=key, parent=self)
            self._errors = self._errors + field._errors

            # don't set __dict__ if they can use any key
            self.__dict__[key] = field
            self._objs[key] = field

    def _as_dict(self):
        # d = {
        #     'active': self.active,
        #     'inactive': self.inactive,
        # }
        d = {}
        for group_name in self._objs.keys():
            d[group_name] = self[group_name]._as_dict()

        d['errors'] = [x.as_dict() for x in self._errors]
        d['valid'] = self.is_valid()
        d.update(self._as_dict_to_inject())

        return d
