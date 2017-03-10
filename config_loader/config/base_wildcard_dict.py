from .base_dict import ConfigBaseDict


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
