LMIShell v2
===========

**The LMIShell v2 was redesigned to serve as a (non)interactive interpreter,
but also as a Python API.  This project's implementation hasn't finished,
yet.**

The OpenLMI project provides a common infrastructure for the management of
Linux systems.  Capabilities include configuration, management and monitoring of
hardware, operating systems, and system services. OpenLMI includes a set of
services that can be accessed both locally and remotely, multiple language
bindings, standard APIs, and standard scripting interfaces.


Dependencies
------------

  * python2.7
  * python-ipython-console
  * python-lmiwbem
  * python-setuptools


Installation
------------

Use standard `setuptools` script for installation:

    $ cd src
    $ python setup.py install --root=/path/to/install/directory

If you have limited access to system path, you may wish to install to user
directory instead:

    $ python setup.py install --user


Bug Reports
===========

Report bugs to **[phatina@redhat.com](mailto:phatina@redhat.com)**
or **[LMIShell issues][]**.

[LMIShell issues]: https://github.com/phatina/lmishell/issues "Report a bug"
