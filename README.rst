
This script will parse RSS feeds from the Dutch government in an attempt to
find publications relevant to the field of digital civil rights and privacy.
Some of the feeds will be included completely, others will be filtered using a
list of keywords. For example, this script is in use at rejo.zenger.nl where it
monitors all documents released at officielebekendmakingen.nl and all press
releases and other documents put to public by the Interior ministry and the
ministry of Justice. 

See: https://rejo.zenger.nl/inzicht/newspeak-van-de-nederlandse-overheid/

This script only needs one MySQL database with two tables. It's structure is
included in the mysql.sql file. The scripts configuration file is included in
feeds.example.cfg, which must be renamed to feeds.cfg. To start monitoring feeds
one adds the row to the feeds table in the database. Of course, one needs to
know the address of the RSS feed to monitor. The column filter denotes whether
the articles from the feed must be filtered ("2") or not ("1"). The description
field is self-explanatory, just like the active field. The format column changes
the order of the output fields (as sometimes we prefer to have the description
field from the input to be the title field on the output). 

When feeds are added, run script on a regular basis from the crontab.

You are free to use and to hack this script. If you have any suggestions, feel
free to send me an e-mail at <rejo.zenger@bof.nl>. Alternatively, fork a branche
at <https://github.com/rejozenger/newspeak> make changes yourself.
