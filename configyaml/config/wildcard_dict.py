from .dict import DictNode


class WildcardDictNode(DictNode):
    def _validate_value(self):
        for key, value in self._value.items():
            # where key name doesn't matter (ex. groups)
            key_valid, explanation = self._key_name_is_valid(key)
            if key_valid:
                field_class = self._dict_fields['*']['class']
                field = field_class(value=value, value_node=self._find_node_for_key_value(key), context=self._context, key=key, parent=self)

                # don't set __dict__ if they can use any key
                self._children[key] = field
            else:
                self._add_error(
                    node=self._find_node_for_key(key),
                    title='Invalid field name',
                    description=explanation
                )

    def _as_dict(self):
        d = {}
        for group_name in self._children.keys():
            d[group_name] = self[group_name]._as_dict()

        if self._errors:
            d['errors'] = [x.as_dict() for x in self._errors]

        d.update(self._as_dict_to_inject())

        return d

    def _key_name_is_valid(self, key):
        if key == '*':
            return False, 'Field name cannot be "*"'

        if key.startswith('_'):
            return False, 'Cannot start field name with a "_"'

        return True, 'Valid'
