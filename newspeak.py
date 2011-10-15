#!/usr/bin/python2.6
"""This script will parse RSS feeds from the Dutch government in an attempt to
find publications relevant to the field of digital civil rights and privacy.
Some of the feeds will be included completely, others will be filtered using a
list of keywords."""

from datetime import datetime
from time import mktime
from ConfigParser import SafeConfigParser
import cgi
import feedparser
import MySQLdb
import PyRSS2Gen
import sys

CONFIG = SafeConfigParser()
CONFIG.read('newspeak.cfg')

# Not including "buma" because it matches the name of a senator.
#
# Removed, because matching too much.
#      '/ digita/i',
#
# There's a space prepending the string, to make sure the match
# won't be made in the middle of a word (e.g. "anpr" matching
# "methaanproductie"). There's no space at the end, as sometimes
# the words match only partial (e.g. "biometri" matching both
# "biometrie" as well as "biometrisch").

KEYWORDS = [' acta',
    ' aftap',
    ' aivd',
    ' anoniem',
    ' anonimiteit',
    ' anpr',
    ' auteursrecht',
    ' bewaarplicht',
    ' biometri',
    ' bits of freedom',
    ' bodyscanners',
    ' cameratoezicht',
    ' centraal informatiepunt onderzoek telecommunicatie',
    ' ciot',
    ' cloud computing',
    ' cookies',
    ' ctivd',
    ' communicatietechnologie',
    ' computer',
    ' copyright',
    ' cyber',
    ' data',
    ' digid',
    ' embed',
    ' fileshar',
    ' filter',
    ' google',
    ' intellectu',
    ' internet',
    ' interoperabiliteit',
    ' ip adres',
    ' ip-adres',
    ' kinderporno',
    ' mensenrechten',
    ' mivd',
    ' netneutraliteit',
    ' ncss',
    ' octrooi',
    ' ov.chipkaart',
    ' patent',
    ' persoonsgegevens',
    ' piracy',
    ' piraterij',
    ' privacy',
    ' provider',
    ' retentie',
    ' retention',
    ' skimmen',
    ' software',
    ' spysoftware',
    ' swift',
    ' telecom',
    ' thuiskopie',
    ' trojan',
    ' vingerafdruk',
    ' voip',
    ' wob']

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

CURSOR.execute('''SELECT id, uri, filter, format FROM feeds
        WHERE active = '1' ''')
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
        items.time_published, feeds.description, feeds.format FROM items, feeds
        WHERE items.feed_id = feeds.id
        AND feeds.active = '1'
        ORDER BY items.time_published DESC
        LIMIT 50''')
PUBLISHED_ITEMS = CURSOR.fetchall()

FEED_ITEMS = [
    PyRSS2Gen.RSSItem(
            title = published_item[1],
            link = published_item[0],
            description = """%s (%s)""" % (published_item[2],
                published_item[4]),
            guid = published_item[0],
            pubDate = published_item[3]
            )
        for published_item in PUBLISHED_ITEMS
    ]

PUBLISHED_FEED = PyRSS2Gen.RSS2(
    title = CONFIG.get('rss', 'title'),
    link = CONFIG.get('rss', 'link'),
    description = CONFIG.get('rss', 'description'),
    managingEditor = CONFIG.get('rss', 'editor'),
    lastBuildDate = datetime.utcnow(),
    items = FEED_ITEMS
    )

PUBLISHED_FEED.write_xml(open(CONFIG.get('files', 'rss'), "w"))


CURSOR.close()
CONN.close()
