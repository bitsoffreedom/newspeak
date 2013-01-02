Newspeak, a composite RSS feed creating script.
===============================================

Use case
--------

I have created this script for personal use, scratching an itch. Here's how I use the script.

This script parses RSS feeds from websites of the Dutch government in an attempt to find publications relevant to the field of digital civil rights and privacy. Some of the feeds will be included in it's completeness, others will be filtered using a list of keywords. Any item that was unknown is stored into a database. On every run, the script will also regenerate a RSS file, listing the most recently added items.

But, with other RSS feeds as input or with other keywords to match, you could probably use this for other purposes as well. 

Configuration
-------------

* This script only needs a MySQL database with two tables. The structure for these tables is included in the mysql.sql file. The scripts' configuration file is included in newspeak.example.cfg, which must be renamed to newspeak.cfg. All fields should be self-explanatory, but are commented as well.

* To start monitoring feeds one adds the row to the feeds table in the database. The column filter denotes whether the articles from the feed must be filtered ("2") or not ("1"). The description field is self-explanatory, just like the active field. The format column changes the order of the output fields (as sometimes we prefer to have the description field from the input to be the title field on the output). If format is set "0" the description field of the item in the source RSS feed will be used as the title field in the item in the composite RSS feed - and the other way around. If format is set to "1", the fields aren't swapped.

* The keywords should go into a separate file: keywords.txt. I am prepending the keywords with a space when I want to make sure it matches the beginning of a word ((e.g. "anpr" matching "methaanproductie"). There's no space at the end, as sometimes the words match only partial (e.g. "biometri" matching both "biometrie" as well as "biometrisch"). Comments starting with "#" are ignored.  

* Finally, edit the templates. There are included two examples. Any file in the templates/ directory is processed as a template. The script will process the variables, using the Cheetah templating engine, then will write a file with an identical name to the directory as specified in the configuration.

When feeds are added, run the script on a regular basis from the crontab.

Variables available in templates
--------------------------------

title
    The title of the composite RSS feed.

description
    The description of the composite RSS feed.

uri_rss
    The URI of the composite RSS feed.

uri_lst
    The URI of the website with additional information on the RSS feed.

editor_addr
    The e-mailaddress of the maintainer of the RSS feed.

editor_name
    The name of the maintainer of the RSS feed.

timestamp
    The timestamp when the script is run.

num_feeds
    The number of source RSS feeds that are monitored.

feeds
    A list of source RSS feeds. Can be used from within a #for loop. It's fields are ID, source URI, whether it is filtered (0 = no, 1 = yes), format (see above), description.

articles
    A list of articles. Can be used from within a #for loop. It's fields are the item's URI, title, description, time of publication at the source RSS feed, the source RSS feed's description and the feeds' filter status.

keywords
    A list of keywords which are used to match insteresting articles in the (filtered) source RSS feeds.

version
    A versionnumber of the code.

Get the code
------------

Fork the code at <https://github.com/rejozenger/newspeak> to make changes.
