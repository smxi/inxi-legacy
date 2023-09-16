====================================================================
README for GetSystemData Perl XS Module
====================================================================

git clone https://codeberg.org/smxi/inxi-legacy

There are 2 directories which must be known a priori to compiling:

1. Location of X header files (Xlib.h, Xatom.h) - defaults to
/usr/X11R6/include.  Specified in Makefile.PL

2. Location of the X libraries.  Defaults to /usr/X11R6/lib. Specified
on command line.

You'll have to confirm the location of these files and adjust
accordingly. In file: Makefile.PL

Change:
INC               => '-I. -I/usr/include/X11'

to path found by: locate Xlib.h

For step 2, make sure /usr/X11R6/lib is the correct path.

Step 5 requires root, and will install to INC path.

To compile/install:

1. cd into GetSystemData/ and type:
2. perl Makefile.PL LIBS='-L/usr/X11R6/lib -lX11'
3. make
4. make test
5. make install

From perl, load module:

use GetSystemData;
$winmgr = GetSystemData::get_wmname;

There are other perl requirements for xsubs that might not be standard
for Linux systems.  For example, the perl header files used to compile
perl must be present on the system.  Don't know if that is really
necessary.
