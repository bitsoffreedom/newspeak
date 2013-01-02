newspeak: Standalone Django based feed aggregator
==================================================

Gettingg started
----------------
Getting started with newspeak is really easy thanks to David Cramer's awesome
`logan <https://github.com/dcramer/logan>` for making standalone Django apps.
Simply perform the following steps:

1. Clone repository.
       git clone <repo_url>
2. Install such that you can easily code along::
       python setup.py develop
3. Initialize configuration in `~/.newspeak/newspeak.conf.py`::
       newspeak init
4. Create admin user and SQLite database (proper database is optional)::
       newspeak syncdb --migrate
5. Start the local webserver::
       newspeak run_gunicorn
6. Open `http://127.0.0.1:8000/admin/` in your browser.
