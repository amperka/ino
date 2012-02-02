===
Ino
===

Ino is a command line toolkit for working with Arduino hardware

It allows you to:

* Quickly create new projects
* Build a firmware from multiple source files and libraries
* Upload the firmware to a device
* Perform serial communication with a device (aka serial monitor)

Ino may replace Arduino IDE UI if you prefer to work with command
line and an editor of your choice or if you want to integrate Arduino
build process to 3-rd party IDE.

Ino is based on ``make`` to perform builds. However Makefiles are
generated automatically and you'll never see them if you don't want to.

Features
========

* Simple. No build scripts are necessary.
* Out-of-source builds. Directories with source files are not
  cluttered with intermediate object files.
* Support for ``*.ino`` and ``*.pde`` sketches as well as
  raw ``*.c`` and ``*.cpp``.
* Support for Arduino Software versions 1.x as well as 0.x.
* Automatic dependency tracking. Referred libraries are automatically
  included in the build process. Changes in ``*.h`` files lead
  to recompilation of sources which include them.
* Pretty colorful output.
* Support for all boards that are supported by Arduino IDE.
* Fast. Discovered tool paths and other stuff is cached across runs. 
  If nothing has changed, nothing is build.
* Flexible. Support for simple ini-style config files to setup
  machine-specific info like used Arduino model, Arduino distribution
  path, etc just once.

Installation
============

From source:

* `Download latest source tarball <http://pypi.python.org/pypi/ino/#downloads>`_
* Or clone it from GitHub: ``git clone git://github.com/amperka/ino.git``
* Do ``make install`` to perform installation under ``/usr/local``
* Or see ``INSTALL`` for instructions on changing destination directory

With Python setup tools:

* Either ``pip install ino``
* Or ``easy_install ino``

Requirements
============

* Python 2.6+
* Arduino IDE distribution
* ``picocom`` for serial communication

Limitations
===========

* As for current version, ino works only in Linux and MacOS.
  However it was created with other OS users in mind,
  so it will eventually get full cross-platform support.
  Help from Windows-developers is much appreciated.

Getting Help
============
    
* Take a look at `Quick start tutorial <http://inotool.org/quickstart>`_.
* Run ``ino --help``.
* Post `issues to GitHub <http://github.com/amperka/ino/issues>`_.

License
=======

If not stated otherwise ino is distributed in terms of MIT software license.
See MIT-LICENSE.txt in the distribution for details.

Changelog
=========

0.3.2
    * Fix #13: Local header #includes from sketch files are no longer lead to
      'No such file or directory' error. Now GCC is given an additional include
      path pointing to the sketch origin while compiling processed source.
    * Fix #18: Proper scanning of dependency files when multiple library
      dependencies are found on the same line. Now all of them are taken into
      account, not just first one.
    * Add: Processed sketch files now have #line directive so that they appear
      as original source in GCC in case of syntax errors.
    * Add: Automatic dependency tracking for included header files. Now a
      sketch or cpp source get rebuild once an included (directly or
      indirectly) header changes.

0.3.1
    * Support for ``ino build --verbose``

0.3.0
    * MacOS support
    * Serial port guess

0.2.0
    * Support for Arduino Software version 1.0

0.1.x
    * Initial release 
    * Various bug fixes
