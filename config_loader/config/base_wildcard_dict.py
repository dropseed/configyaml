from .base_dict import ConfigBaseDict


class ConfigBaseWildcardDict(ConfigBaseDict):
    def _validate_value(self):
        for key in self._value.keys():
            # where key name doesn't matter (ex. groups)
            field_class = self._dict_fields['*']['class']
            field = field_class(value=self._value[key], value_node=self._find_node_for_key_value(key), context=self._context, key=key, parent=self)

            # don't set __dict__ if they can use any key
            self._children[key] = field

    def _as_dict(self):
        d = {}
        for group_name in self._children.keys():
            d[group_name] = self[group_name]._as_dict()

        if self._errors:
            d['errors'] = [x.as_dict() for x in self._errors]

        d.update(self._as_dict_to_inject())

        return d
