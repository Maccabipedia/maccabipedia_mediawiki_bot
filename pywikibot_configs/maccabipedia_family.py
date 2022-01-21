# -*- coding: utf-8 -*-
"""
This family file was auto-generated by generate_family_file.py script.

Configuration parameters:
  url = https://www.maccabipedia.co.il
  name = maccabipedia

Please do not commit this to the Git repository!
"""
from __future__ import absolute_import, division, unicode_literals

from pywikibot import family
from pywikibot.tools import deprecated


class Family(family.Family):  # noqa: D101

    name = 'maccabipedia'
    langs = {
        'he': 'www.maccabipedia.co.il',
    }

    def scriptpath(self, code):
        return {
            'he': '',
        }[code]

    @deprecated('APISite.version()', since='20141225')
    def version(self, code):
        return {
            'he': '1.31.0',
        }[code]

    def protocol(self, code):
        return {
            'he': 'https',
        }[code]
