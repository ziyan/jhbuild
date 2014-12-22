# jhbuild - a tool to ease building collections of source packages
# Copyright (C) 2014 Canonical Limited
#
#  sysid.py: identify the system that we are running on
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the licence, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys
import subprocess
import ast

sys_id = None
sys_name = None

def read_os_release():
    global sys_name
    global sys_id

    release_file = None

    try:
        release_file = open('/etc/os-release')
    except:
        try:
            release_file = open('/usr/lib/os-release')
        except:
            return False

    fields = {}
    for line in release_file:
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        if '=' not in line:
            continue

        field, _, value = line.partition('=')

        if value.startswith("'") or value.startswith('"'):
            try:
                value = ast.literal_eval(value)
            except:
                continue

        fields[field] = value

    if 'ID' not in fields or 'VERSION_ID' not in fields:
        return False

    sys_id = fields['ID'] + '-' + fields['VERSION_ID']

    if 'NAME' in fields and 'VERSION' in fields:
        sys_name = fields['NAME'] + ' ' + fields['VERSION']
    else:
        # fall back
        sys_name = fields['ID'] + ' ' + fields['VERSION_ID']

    return True

def get_macos_info():
    global sys_name
    global sys_id

    try:
        ver = subprocess.check_output('sw_vers -productVersion')

        sys_name = 'Mac OS X ' + ver
        sys_id = 'macos-' + ver

        return True

    except:
        return False

def ensure_loaded():
    global sys_name
    global sys_id

    if sys_id is not None:
        return

    # our first choice is to use os-release info
    if read_os_release():
        return

    # but failing that, fall back to using sys.platform
    sys_id = sys.platform

    if sys_id.startswith('linux'):
        sys_name = "Unknown Linux Distribution (no 'os-release' file)"

    elif sys_id.startswith('freebsd'):
        sys_name = 'FreeBSD (%s)' % (sys_id)

    elif sys_id.startswith('macos'):
        if not get_macos_info():
            sys_name = 'Mac OS X (unknown version)'

    else:
        sys_id = sys.platform
        sys_name = sys.platform

def get_id():
    ensure_loaded()

    return sys_id

def get_pretty_name():
    ensure_loaded()

    return sys_name
