#!/usr/bin/python2.6
"""This script will parse RSS feeds from the Dutch government in an attempt to
find publications relevant to the field of digital civil rights and privacy.
Some of the feeds will be included completely, others will be filtered using a
list of keywords."""

from datetime import datetime
from time import mktime
from email import Utils
from ConfigParser import SafeConfigParser
from Cheetah.Template import Template
import cgi
import feedparser
import MySQLdb
import os
import sys

CONFIG = SafeConfigParser()
CONFIG.read('newspeak.cfg')

KEYWORDS = []
with open('keywords.txt', 'r') as f:
    for line in f:
        line = line.partition('#')[0]
        if line != '':
            KEYWORDS.append(line.rstrip())

try:
    CONN = MySQLdb.connect(host = CONFIG.get('database', 'hostname'),
            user = CONFIG.get('database', 'username'),
            passwd = CONFIG.get('database', 'password'),
            db = CONFIG.get('database', 'database'),
            charset = CONFIG.get('database', 'charset'))

except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

CURSOR = CONN.cursor()

def convert_unicode_to_html(string):
    """Converts unicode to HTML entities. For example '&' becomes '&amp;'."""
    string = cgi.escape(string).encode('ascii', 'xmlcharrefreplace')
    return string

def does_match_keyword(item):
    """Return TRUE if the string contains any of the given keywords."""
    for key in KEYWORDS:
        if key in item['title'].lower() or key in item['description'].lower():
            return True
    return False

def is_existing_item(link):
    """See if URI of item is already known in the database."""
    CURSOR.execute('''SELECT id FROM items WHERE link = %s''', link)
    return CURSOR.rowcount > 0

def insert_item_into_db(link, feed_id, title, description, updated_parsed,
        feed_format):
    """Add a new item to the database."""
    if feed_format == '0':
        CURSOR.execute('''INSERT INTO items (link, feed_id, title,
                description, time_published) VALUES (%s, %s, %s, %s,
                %s)''', (link, feed_id,
                    convert_unicode_to_html(description)[0:1000],
                    convert_unicode_to_html(title)[0:1000],
                    datetime.fromtimestamp(mktime(updated_parsed))))
    if feed_format == '1':
        CURSOR.execute('''INSERT INTO items (link, feed_id, title,
                description, time_published) VALUES (%s, %s, %s, %s,
                %s)''', (link, feed_id, convert_unicode_to_html(title)[0:1000],
                    convert_unicode_to_html(description)[0:1000],
                    datetime.fromtimestamp(mktime(updated_parsed))))

CURSOR.execute('''SELECT id, uri, filter, format, description FROM feeds
        WHERE active = '1' ORDER BY 'description' ''')
FEEDS = CURSOR.fetchall()

for feed in FEEDS:
    f = feedparser.parse('%s' % feed[1])
    if feed[2] == '1':
        for item in f.entries:
            if is_existing_item(item['link']) is not True:
                insert_item_into_db(item['link'], feed[0], item['title'],
                        item['description'], item['updated_parsed'], feed[3])
    elif feed[2] == '2':
        for item in f.entries:
            if does_match_keyword(item) is True:
                if is_existing_item(item['link']) is not True:
                    insert_item_into_db(item['link'], feed[0], item['title'],
                            item['description'], item['updated_parsed'],
                            feed[3])

CURSOR.execute('''SELECT items.link, items.title, items.description,
                DATE_FORMAT(items.time_published,'%a, %d %b %Y %T CET'),
                feeds.description, feeds.format
                FROM items, feeds WHERE items.feed_id = feeds.id AND
                feeds.active = '1' ORDER BY items.time_published
                DESC LIMIT 50''')
ITEMS = CURSOR.fetchall()

TMPL_VARS = { "title":CONFIG.get('output', 'title'),
    "description":CONFIG.get('output', 'description'),
    "uri_rss":CONFIG.get('output', 'uri_rss'),
    "uri_lst":CONFIG.get('output', 'uri_lst'),
    "editor_addr":CONFIG.get('output', 'editor_addr'),
    "editor_name":CONFIG.get('output', 'editor_name'),
    "timestamp":Utils.formatdate(localtime=True),
    "num_feeds":len(FEEDS),
    "feeds":FEEDS,
    "articles":ITEMS,
    "keywords":KEYWORDS,
    "version":"Newspeak 0.0"
    }

FILES = os.listdir('templates/')
for file in FILES:
    CONTENT = Template(file='templates/%s' % (file), searchList=[TMPL_VARS])
    OUTPUT = open('%s/%s' % (CONFIG.get('output', 'directory'), file), 'w')
    OUTPUT.write(str(CONTENT))
    OUTPUT.close()

CURSOR.close()
CONN.close()
