from .base import ConfigBase


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
