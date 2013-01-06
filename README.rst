newspeak: Standalone Django based feed aggregator
==================================================

Gettingg started
----------------
Getting started with newspeak is really easy thanks to David Cramer's awesome
`logan <https://github.com/dcramer/logan>`_ for making standalone Django apps.
Simply perform the following steps:

#. Install such that you can easily code along::

       pip install -e \
         git+https://github.com/bitsoffreedom/newspeak.git@standalone#egg=newspeak

#. Initialize configuration in `~/.newspeak/newspeak.conf.py`::

       newspeak init

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

Note: alternatively, the original feeds and keywords used by Bits of Freedom
are contained in a fixture called `feeds_keywords_bof.json`. This fixture
can be loaded using::

    newspeak loaddata feeds_keywords_bof

After this running `update_feeds` should give a nice idea of what this package
is capable of.
