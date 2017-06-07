configyaml
==========

.. image:: https://travis-ci.org/dropseedlabs/configyaml.svg?branch=master
    :target: https://travis-ci.org/dropseedlabs/configyaml

.. image:: https://img.shields.io/pypi/v/configyaml.svg
    :target: https://pypi.python.org/pypi/configyaml

.. image:: https://img.shields.io/pypi/l/configyaml.svg
    :target: https://pypi.python.org/pypi/configyaml

.. image:: https://img.shields.io/pypi/pyversions/configyaml.svg
    :target: https://pypi.python.org/pypi/configyaml
    

Usage
-----
The basic usage pattern is to extend these classes to create your own.

You need a loader:

.. code-block:: python

    from configyaml import loader

    from .config.root import Root

    class SibbellConfigLoader(loader.ConfigLoader):
        config_root_class = Root


Then design your config using additional classes. You need at least 1 to serve as the root class:

.. code-block:: python

    from configyaml.config import DictNode
    from .dependencies import Dependencies
    from .notifications import Notifications


    class Root(DictNode):
        """Root of the yaml file"""

        def __init__(self, *args, **kwargs):
            self._dict_fields = {
                        'dependencies': {
                            'class': Dependencies,
                            'required': True,
                            'default': [],
                        },
                        'notifications': {
                            'class': Notifications,
                            'required': True,  # no point right now if no notifications
                            'default': [],
                        }
                    }
            super(Root, self).__init__(*args, **kwargs)

        def _context_to_inject(self):
            """Make dependencies list available to notifcations"""
            return {'dependencies': self.dependencies}

Then to use it, simply create a loader using the configuration text content:

.. code-block:: python

    loader = SibbellConfigLoader(yaml_text)
    # can now access the configuration and any other properties/method added to their classes
    loader.is_valid()
    loader.errors
    loader.config_root.dependencies

