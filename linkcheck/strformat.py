# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Various string utility functions. Note that these functions are not
necessarily optimised for large strings, so use with care.
"""

import re
import textwrap
import sys
import os
import time
import urlparse


def unicode_safe (s, encoding="iso-8859-1"):
    """
    Get unicode string without raising encoding errors. Unknown
    characters of the given encoding will be ignored.

    @param s: the string to be decoded
    @type s: unicode or encoded string
    @return: if s is already unicode, return s unchanged; else return
        decoded unicode string
    @rtype: unicode
    """
    assert s is not None, "argument to unicode_safe was None"
    if isinstance(s, unicode):
        # s is already unicode, nothing to do
        return s
    return unicode(s, encoding, "ignore")


def url_unicode_split (url):
    """
    Like urlparse.urlsplit(), but always returning unicode parts.
    """
    return [unicode_safe(s) for s in urlparse.urlsplit(url)]


def unquote (s):
    """
    Remove leading and ending quotes.

    @return: if s evaluates to False, return s as is, else return
        string with stripped quotes
    @rtype: string or type of s if evaluting to False
    """
    if not s:
        return s
    if len(s) < 2:
        return s
    if s[0] in ("\"'"):
        s = s[1:]
    if s[-1] in ("\"'"):
        s = s[:-1]
    return s


_para_mac = r"(?:%(sep)s)(?:(?:%(sep)s)\s*)+" % {'sep': '\r'}
_para_posix = r"(?:%(sep)s)(?:(?:%(sep)s)\s*)+" % {'sep': '\n'}
_para_win = r"(?:%(sep)s)(?:(?:%(sep)s)\s*)+" % {'sep': '\r\n'}
_para_ro = re.compile("%s|%s|%s" % (_para_mac, _para_posix, _para_win))

def get_paragraphs (text):
    """
    A new paragraph is considered to start at a line which follows
    one or more blank lines (lines containing nothing or just spaces).
    The first line of the text also starts a paragraph.
    """
    if not text:
        return []
    return _para_ro.split(text)


def wrap (text, width, **kwargs):
    """
    Adjust lines of text to be not longer than width. The text will be
    returned unmodified if width <= 0.
    See textwrap.wrap() for a list of supported kwargs.
    Returns text with lines no longer than given width.
    """
    if width <= 0 or not text:
        return text
    ret = []
    for para in get_paragraphs(text):
        ret.extend(textwrap.wrap(para.strip(), width, **kwargs))
    return os.linesep.join(ret)


def get_line_number (s, index):
    """
    Return the line number of s[index]. Lines are assumed to be separated
    by the ASCII character '\\n'.
    """
    i = 0
    if index < 0:
        index = 0
    line = 1
    while i < index:
        if s[i] == '\n':
            line += 1
        i += 1
    return line


def paginate (text, lines=22):
    """
    Print text in pages of lines.
    """
    curline = 1
    for line in text.splitlines():
        print line
        curline += 1
        isatty = hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
        if curline >= lines and isatty:
            curline = 1
            print "press return to continue..."
            sys.stdin.read(1)


_markup_re = re.compile("<.*?>", re.DOTALL)

def remove_markup (s):
    """
    Remove all <*> html markup tags from s.
    """
    mo = _markup_re.search(s)
    while mo:
        s = s[0:mo.start()] + s[mo.end():]
        mo = _markup_re.search(s)
    return s


def strsize (b):
    """
    Return human representation of bytes b. A negative number of bytes
    raises a value error.
    """
    if b < 0:
        raise ValueError, "Invalid negative byte number"
    if b == 1:
        return u"%d Byte" % b
    if b < 1024:
        return u"%d Bytes" % b
    b /= 1024.0
    if b < 1024:
        return u"%.2f kB" % b
    b /= 1024.0
    if b < 1024:
        return u"%.2f MB" % b
    b /= 1024.0
    return u"%.2f GB"


def strtime (t):
    """
    Return ISO 8601 formatted time.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) + \
           strtimezone()


def strduration (duration):
    """
    Return translated and formatted time duration.
    """
    name = _("seconds")
    if duration > 60:
        duration = duration / 60
        name = _("minutes")
    if duration > 60:
        duration = duration / 60
        name = _("hours")
    return u" %.3f %s" % (duration, name)


def strtimezone ():
    """
    Return timezone info, %z on some platforms, but not supported on all.
    """
    if time.daylight:
        zone = time.altzone
    else:
        zone = time.timezone
    return "%+04d" % int(-zone/3600)
