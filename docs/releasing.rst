======================
Releasing This Package
======================

To release new versions of this package we've started using the `zest.releaser`_ script.

Prior to releasing it is good to run the ``lasttaglog`` command to review the git commit logs since the last tag.
These should be used to update the HISTORY.rst file with a human readable changelog.

We do *fullrelease* commands from the master branch.  This command in turn does 3 steps, as documented in the
`zest.releaser documentation`_.

    #. **Prerelease**: Strips the ``-dev0`` component from the version string in ``setup.py``, commits to git

    #. **Release**: Tags in git/GitHub, builds tarball & wheel, uploads to PyPI (with user confirmation)

    #. **Postrelease**: Bumps version number, addes "-dev0" to version string, adds new section to HISTORY.rst


Following this, the release notes added for this version should be used to draft a new `GitHub Release`_ for
the new version.

.. _`zest.releaser`: https://github.com/zeit/release
.. _`zest.releaser documentation`: http://zestreleaser.readthedocs.io/en/latest/overview.html#available-commands
.. _`GitHub Release`: https://github.com/dropseedlabs/configyaml/releases
