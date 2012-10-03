
How I am using this script:

This script will parse RSS feeds from the Dutch government in an attempt to
find publications relevant to the field of digital civil rights and privacy.
Some of the feeds will be included completely, others will be filtered using a
list of keywords. For example, this script is in use at rejo.zenger.nl where it
monitors all documents released at officielebekendmakingen.nl and all press
releases and other documents put to public by the Interior ministry and the
ministry of Justice. 

See: https://rejo.zenger.nl/inzicht/newspeak-van-de-nederlandse-overheid/

But, with other RSS feeds as input or with other keywords to match, you could
probably use this for other purposes as well. 

This script only needs one MySQL database with two tables. It's structure is
included in the mysql.sql file. The scripts' configuration file is included in
newspeak.example.cfg, which must be renamed to newspeak.cfg. 

To start monitoring feeds one adds the row to the feeds table in the database.
The column filter denotes whether the articles from the feed must be filtered
("2") or not ("1"). The description field is self-explanatory, just like the
active field. The format column changes the order of the output fields (as
sometimes we prefer to have the description field from the input to be the title
field on the output). 

The keywords should go into a separate file: keywords.txt. I am prepending the
keywords with a space when I want to make sure it matches the beginning of a
word ((e.g. "anpr" matching "methaanproductie"). There's no space at the end, as
sometimes the words match only partial (e.g. "biometri" matching both
"biometrie" as well as "biometrisch"). Comments starting with "#" are ignored.

When feeds are added, run the script on a regular basis from the crontab.

Fork the code at <https://github.com/rejozenger/newspeak> to make changes.
