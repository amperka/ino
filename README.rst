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
* Support for ``*.pde`` and ``*.ino`` sketches as well as
  raw ``*.c`` and ``*.cpp``.
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

With python setup tools::
    
    $ sudo pip install ino
    # ... or ...
    $ sudo easy_install ino

Or clone from GitHub::

    $ git clone git://github.com/amperka/ino.git
    $ export PATH=`pwd`/ino/bin

Requirements
============

* Python 2.6+
* Arduino IDE distribution
* ``make`` and ``avr-gcc`` for building
* ``picocom`` for serial communication

Limitations
===========

* As for current version, ino works only in Linux. However it was created
  with other platform users in mind, so it will eventually get
  cross-platform support. Help from Windows- and MacOS- developers is
  much appreciated.
* Ino is not yet well tested with release candidate of upcoming Arduino 1.0
  software. Although it should be compatible.

Getting Help
============
    
* Take a look at `Quick start tutorial <http://inotool.org/quickstart>`_.
* Run ``ino --help``.
* Post `issues to GitHub <http://github.com/amperka/ino/issues>`_.

License
=======

If not stated otherwise ino is distributed in terms of MIT software license.
See MIT-LICENSE.txt in the distribution for details.
