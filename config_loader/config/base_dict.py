from .base import ConfigBase


class ConfigBaseDict(ConfigBase):
    def __init__(self, *args, **kwargs):
        self._type = dict
        self._children = {}
        super(ConfigBaseDict, self).__init__(*args, **kwargs)

    def _validate_value(self):
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
            self._children[k] = self._dict_fields[k]['class'](value={})

        for key in keys:
            is_valid, is_valid_explanation = valid_key_name(key)
            if key in available_keys and is_valid:
                # get class for key
                field_class = self._dict_fields[key]['class']
                field = field_class(value=self._value[key], value_node=self._find_node_for_key_value(key), context=self._context, parent=self)

                # set self.FIELD_NAME so we can get children directly
                # these will only be keys we specify, so should be safe names
                self.__dict__[key] = field
                self._children[key] = field

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
