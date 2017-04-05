======================
Releasing This Package
======================

To release new versions of this package we've started using the zest.releaser script.

We do "fullrelease" commands from the master branch.  This command in turn does 3 steps, as documented in the
zest.releaser documentation.

Prerelease
----------

Strips the "-dev0" component from the version string in `setup.py`

Release
-------

Tags/Releases in git/GitHub, builds tarball & wheel, uploads to PyPI (with user confirmation).

Postrelease
-----------

Bumps version number, addes "-dev0" to version string, adds new section to HISTORY.rst



