from .base import AbstractNode


class ListNode(AbstractNode):
    _list_item_class = None

    def __init__(self, *args, **kwargs):
        self._type = list
        self._children = []  # so we can append, etc

        if not hasattr(self, '_min_items_required'):
            # by default, don't have to have anything
            # set to 1 in custom __init__ to require at least 1 item
            self._min_items_required = 0

        if not self._list_item_class:
            raise AttributeError('_list_item_class must be defined in subclasses of ListNode')

        super(ListNode, self).__init__(*args, **kwargs)

    def _validate_value(self):
        if len(self._value) < self._min_items_required:
            self._add_error(
                title='Minimum items requirement not met',
                description='Must have at least {} item(s)'.format(self._min_items_required)
            )

        for index, item in enumerate(self._value):
            field_class = self._list_item_class
            field = field_class(value=item, value_node=self._find_node_for_list_index(index), context=self._context, parent=self, key=index)

            self._children.append(field)

    def _find_node_for_list_index(self, index):
        if not self._value_node:
            return None

        return self._value_node.value[index]

    def __getitem__(self, key):
        return self._children[key]

    def __len__(self):
        return len(self._children)

    def _as_dict(self):
        d = {
            'items': [x._as_dict() for x in self._children],
        }

        if self._errors:
            d['errors'] = [x.as_dict() for x in self._errors]

        d.update(self._as_dict_to_inject())
        return d
