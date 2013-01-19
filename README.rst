newspeak: Standalone Django based feed aggregator
==================================================

What it does
------------
Newspeak is a feed aggregator with advanced features for keyword filtering
and link content extraction, implemented as a standaloone Django application.

Architecture
------------
Newspeak performs the following tasks (in order):

#. Fetch specified RSS/Atom feeds as per the `Feed <https://github.com/bitsoffreedom/newspeak/blob/standalone/src/newspeak/models.py#L70>`_ model (in parallel).
#. Parses the feeds using `feedparser <http://pypi.python.org/pypi/feedparser>`_.
#. (Optionally) applies per-feed inclusive/exclusive keyword filters on the title and/or summary, based on the `KeywordFilter <https://github.com/bitsoffreedom/newspeak/blob/standalone/src/newspeak/models.py#L8>`_ model.
#. (Optionally) extract summary data using an XPath expression from feed entry's link URL, using `lxml <http://lxml.de/>`_.
#. (Optionally) extract enclosure information using XPath expressions from the feed entry's link URL, using `lxml <http://lxml.de/>`_.
#. Store the resulting feed information locally in a database.
#. Serve the aggregate of all the feed entries in a single RSS/Atom feed.

The flow of feed data through the application is roughly as follows (given some example feeds and keyword filters)::

    [Feed 1]-[Keyword filter 1]-[Keyword filter 2]-[XPath content extraction]-----------------------------`\
    [Feed 2]--------------------[Keyword filter 3]-[XPath summary extraction]-[XPath content extraction ] -+--[Aggregate output feed]
    [Feed 3]-[Keyword filter 3]-[Keyword filter 4]---------------------------------------------------------/

Installing
----------------
Getting started with newspeak is really easy thanks to David Cramer's awesome
`logan <https://github.com/dcramer/logan>`_ for making standalone Django apps.
Simply perform the following steps:

#. Install such that you can easily code along::

       pip install -e \
         git+https://github.com/bitsoffreedom/newspeak.git@standalone#egg=newspeak

   If you're smart and like to keep your Python environment clean, do this
   in a `VirtualEnv <http://pypi.python.org/pypi/virtualenv/>`_.

#. Initialize configuration in `~/.newspeak/newspeak.conf.py`::

       newspeak init

#. (Optionally) Run the tests::

       newspeak test newspeak

   This might take a while, so go fetch a cup of coffee. If something fails,
   please supply the output of the command `newspeak test newspeak --traceback`
   in an [issue](https://github.com/bitsoffreedom/newspeak/issues) on GitHub.

#. Create admin user and SQLite database (proper database is optional)::

       newspeak syncdb --migrate

#. Start the local webserver::

       newspeak run_gunicorn

#. Open `http://127.0.0.1:8000/admin/` in your browser, add some feed. Only
   the URL is required, the description and title will be fetched
   automatically, as well as the first set of entries.

#. (Optionally) Configure one or more keyword-based filters for your feed(s).

#. Make sure the following command gets executed to update the feeds::

       newspeak update_feeds

   (Optionally, add `-v <1|2|3>` to get more feedback on the process.)

#. Look at the pretty feeds: open `http://127.0.0.1:8000/all/rss/` or
   `http://127.0.0.1:8000/all/atom/` in your favorite feed reader. All input
   feeds will be aggregated there.

   Alternatively, the original feeds and keywords used by Bits of Freedom
   are contained in a fixture called `feeds_keywords_bof.json`. This fixture
   can be loaded using::

       newspeak loaddata feeds_keywords_bof

#. Setup a `Cronjob <http://en.wikipedia.org/wiki/Cronjob>`_ to automatically 
   update the feed data using the `newspeak update_feeds` command. For 
   example, a cron job updating the feeds every hour could look as follows::

       0 * * * *  <full_path_to_>/newspeak update_feeds

Upgrading
----------
#. Run the PIP installation command again::

       pip install -e \
         git+https://github.com/bitsoffreedom/newspeak.git@standalone#egg=newspeak

#. (Optionally) Run the tests::

       newspeak test newspeak

#. Apply any database migrations::

       newspeak migrate

