from .base import AbstractNode


class DictNode(AbstractNode):
    def __init__(self, *args, **kwargs):
        self._type = dict
        self._children = {}
        super(DictNode, self).__init__(*args, **kwargs)

    def _validate_value(self):
        self._validate_required_keys()
        self._set_default_fields()

        for key, value in self._value.items():

            if key in self._dict_fields:
                # get class for key
                field_class = self._dict_fields[key]['class']
                field = field_class(value=self._value[key], value_node=self._find_node_for_key_value(key), context=self._context, key=key, parent=self)

                # set self.FIELD_NAME so we can get children directly
                # these will only be keys we specify, so should be safe names
                self.__dict__[key] = field
                self._children[key] = field
            else:
                # cannot use key
                self._add_error(
                    node=self._find_node_for_key(key),
                    title='Invalid key',
                    description='Available fields are: {}'.format(', '.join(sorted(self._dict_fields.keys()))),
                )

    def _validate_required_keys(self):
        required_keys = [k for k, v in self._dict_fields.items() if v.get('required', False)]
        for k in required_keys:
            if k not in self._value:
                self._add_error(
                    title='Required field is missing',
                    description='{} is a required field'.format(k)
                )

    def _set_default_fields(self):
        for k, v in self._dict_fields.items():
            if 'default' in v:
                default = v['default']
                instance = v['class'](value=default, context=self._context, key=k, parent=self)
                self.__dict__[k] = instance
                self._children[k] = instance

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
        return self._children[key]

    def __len__(self):
        return len(self._children)

    def _as_dict(self):
        d = {}
        for k in self._dict_fields.keys():
            d[k] = self[k]._as_dict()

        if self._errors:
            d['errors'] = [x.as_dict() for x in self._errors]

        d.update(self._as_dict_to_inject())

        return d
