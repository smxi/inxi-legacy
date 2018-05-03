#define PERL_NO_GET_CONTEXT
#include "EXTERN.h"
#include "perl.h"
#include "XSUB.h"

#include "ppport.h"

#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>

char *get_wmname(void);

MODULE = GetSystemData		PACKAGE = GetSystemData		
PROTOTYPES: ENABLE

char *
get_wmname()

	PREINIT:
	Display *disp;
	Window *sup_window;
	char *wm_name;
	char *name;
	unsigned long ret_nitems;
	unsigned long ret_bytes_after;
	unsigned long len;
	unsigned char *ret_prop;
	Atom a_pname;
	Atom a_rettype;
	int ret_format;

	CODE:

	sup_window = NULL;
	wm_name = NULL;


	if (! (disp = XOpenDisplay(NULL))) {
	    fputs("Cannot open display.\n", stderr);
	    wm_name = NULL;
	}

	a_pname = XInternAtom(disp, "_NET_SUPPORTING_WM_CHECK", False);
	XGetWindowProperty(disp, DefaultRootWindow(disp), a_pname, \
	    0, 1024, False, XA_WINDOW, &a_rettype, \
	    &ret_format, &ret_nitems, &ret_bytes_after, &ret_prop);

	if (a_rettype != XA_WINDOW) {
		printf("Invalid type property.\n");
	}

	len = (ret_format / 8) * ret_nitems;
	name = malloc((ret_format / 8 * ret_nitems) + 1);
	memcpy(name, ret_prop, len);
	name[len] = '\0';    
	sup_window = (Window *)name;

	a_pname = XInternAtom(disp, "_NET_WM_NAME", False);
	if (XGetWindowProperty(disp, *sup_window, a_pname, 0, 1024, False, \
	    XInternAtom(disp, "UTF8_STRING", False), &a_rettype, &ret_format, \
	    &ret_nitems, &ret_bytes_after, &ret_prop) != Success) {

	    printf("Cannot get WM property.\n");
	    exit (-1);
	}

	len = (ret_format / 8) * ret_nitems;
	wm_name = malloc(len + 1);
	memcpy(wm_name, ret_prop, len);
	wm_name[len] = '\0';
	XFree(ret_prop);
	free(name);
	XCloseDisplay(disp);
	
	RETVAL = wm_name;

	OUTPUT:
	    RETVAL

