#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Jason Hu'
SITENAME = u"Jason Hu's Blog"
SITEURL = ''

ARTICLE_SAVE_AS = '{date:%Y}/{slug}.html'
ARTICLE_URL = '{date:%Y}/{slug}.html'
PATH = 'content'

TIMEZONE = 'America/Toronto'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

PLUGIN_PATHS = ['plugins']
PLUGINS = ["render_math"]

FILENAME_METADATA = '(?P<slug>.*)'

SHOW_CREDITS = {
    'left': 'theme modified based on <a href="https://github.com/arulrajnet/attila" rel="nofollow">Attila</a>'}

DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = True
HEADER_COVER = 'images/cover.png'
HEADER_COLOR = "#32A4D4"

MENUITEMS = [
    ('Tags', '{}/tags.html'.format(SITEURL)),
    ('Categories', '{}/categories.html'.format(SITEURL))
]

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
