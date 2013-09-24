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

Contributors
============

* `David Charbonnier <https://github.com/dcharbonnier>`_.
* `Jared Boone <https://github.com/jboone>`_.
* `Lars Englund <https://github.com/larsenglund>`_.
* `Alberto Ruiz <https://github.com/aruiz>`_.
* `12qu <https://github.com/12qu>`_.
* `Michael Sproul <https://github.com/gnusouth>`_.
* `Marc Plano-Lesay <https://github.com/Kernald>`_.
* `Fabian Kreiser <https://github.com/fabiankr>`_.

Changelog
=========

0.3.6
    * Fix #74, #107, #108: Use of types declared in included files is allowed
      in function definitions. Previously it led to: '<enum|struct|typedef>' not
      declared in this scope.
    * Fix #105: Search for `avrdude.conf` in `/etc/avrdude` to be compatible with
      Fedora.
    * Fix #99: Check for an existing project before building or creating directories
    * Fix #93, #57, #8: Custom compile and link flags can be passed as `ino build` arguments
    * Fix #60, #63: Custom `make` tool command can be passed as `ino build` argument
    * Fix #23, #28: `make` is searched within Arduino IDE binaries as well
    * Fix #88, #103: Correct version parsing for some distributions that mangle it
    * Fix #46: Taking build number into account in version string
    * Fix #19, #81, #82: Custom command line arguments for `picocom` can be passed
      while running `ino serial`

0.3.5
    * Fix #62: Include `MIT-LICENSE.txt` in the tarball.

0.3.4
    * Fix #44, #45: Building and uploading for Arduino Leonardo is fully supported.
    * Fix #3, #29: Build artifacts for different board models and Arduino distributions
      go in different build subdirectories, so you haven't to run ``ino clean`` and
      rebuild if you switch to another Arduino model or software distribution.
    * The version of avr gcc toolset that is bundled with Arduino Software is now
      always preferred over system-wide. So that users with edge-versions of software
      (such as Arch Linux) able to produce expected results.

0.3.3
    * Fix #16: ``*.ino`` and ``*.pde`` sketches are now populated with function
      prototypes while preprocessing step in the same way as it done by Arduino IDE,
      so it is now possible to use functions before they're declared or defined.

0.3.2
    * Fix #13: Local header #includes from sketch files are no longer lead to
      'No such file or directory' error. Now GCC is given an additional include
      path pointing to the sketch origin while compiling processed source.
    * Fix #18: Proper scanning of dependency files when multiple library
      dependencies are found on the same line. Now all of them are taken into
      account, not just first one.
    * Add: Processed sketch files now have #line directive so that they appear
      as original source in GCC output in case of syntax errors.
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
