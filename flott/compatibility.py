#!/usr/bin/env python
# -*- coding: utf-8 -*-

#----------------------------------------------------------------------------------------------------------------------------------
# includes

# 2+3 compat
from __future__ import absolute_import, division, print_function, unicode_literals

# standards
from sys import version_info

#----------------------------------------------------------------------------------------------------------------------------------

PY2 = version_info[0] == 2

if PY2:
    execfile = execfile
else:
    def execfile(filename, globals=None, locals=None):
        with open(filename) as handle:
            exec(
                compile(
                    handle.read(),
                    filename,
                    'exec',
                ),
                globals,
                locals
            )

#----------------------------------------------------------------------------------------------------------------------------------
