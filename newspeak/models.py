import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.conf.global_settings import LANGUAGES


class KeywordFilter(models.Model):
    """ A keyword-based filter to be used when importing feeds. """

    class Meta:
        verbose_name = _('keyword filter')
        verbose_name_plural = _('keyword filters')

    name = models.CharField(_('name'), max_length=255)
    active = models.BooleanField(_('active'), default=True, db_index=True)

    keywords = models.TextField(_('keywords'),
        help_text=_(
            'Keywords to filter by, seperated by comma\'s. Shell-style '
            'wildcards can be used: "chee*" will match both "cheese" as '
            'well as "cheetah".'
        )
    )

    # Filter specs
    filter_inclusive = models.BooleanField(_('filter inclusive'),
        help_text=_('Whether to perform inclusive or exclusive filtering.'),
        default=True)
    filter_title = models.BooleanField(_('filter title'), default=True)
    filter_summary = models.BooleanField(_('filter summary'), default=True)

    def __unicode__(self):
        return self.name


class Feed(models.Model):
    """
    A Feed represents an Atom or RSS feed resource to be aggregated.
    """

    class Meta:
        verbose_name = _('feed')
        verbose_name_plural = _('feeds')

    title = models.CharField(_('title'), max_length=1024, blank=True)
    subtitle = models.CharField(_('subtitle'), max_length=1024, blank=True)
    link = models.URLField(_('link'), max_length=330, blank=True)
    url = models.URLField(_('URL'), max_length=330)

    # feed_id = models.CharField(_('remote feed id'),
    #     unique=True, editable=False, max_length=255)

    updated = models.DateTimeField(_('time updated'),
            editable=False, null=True)

    description = models.TextField(_('description'), blank=True)
    active = models.BooleanField(_('active'), default=True, db_index=True)
    filters = models.ManyToManyField(KeywordFilter, null=True, blank=True)

    """ Preserve error state. """
    error_state = models.BooleanField(
        _('error'), help_text=_('Latest crawl yielded error.'),
        default=False, db_index=True, editable=False)
    error_description = models.TextField(_('error description'),
        help_text=_('Description of latest crawl error.'), editable=False)
    error_date = models.DateTimeField(_('error date'), null=True,
        help_text=_('Latest time when an error was seen.'), editable=False)

    """ HTTP 1.1 get optimizations """
    modified = models.CharField(_('HTTP Last Modified header'),
        max_length=255, editable=False)
    etag = models.CharField(_('HTTP Etag'),
        max_length=255, editable=False)

    """ XPath summary extraction. """
    summary_xpath = models.CharField(_('summary XPath'), blank=True,
        help_text=_('XPath expression to find the summary content. Leave '
                    'blank to disable extraction.'), max_length=1024)
    summary_override = models.BooleanField(_('override summary'),
        help_text=_('Whether or not to override existing summaries with '
                    'extracted values.'), default=False)

    """ XPath content extraction. """
    content_xpath = models.CharField(_('content XPath'), blank=True,
        help_text=_('XPath expression to find the extracted content. Leave '
                    'blank to disable extraction.'), max_length=1024)

    # Feeds only allow a small selection of content types
    CONTENT_MIME_TYPE_CHOICES = (
        ('text/plain', _('Text')),
        ('text/html', _('HTML')),
        ('application/xhtml+xml', _('XHTML'))
    )
    content_mime_type = models.CharField('content MIME type', blank=True,
        help_text=_('MIME type to use for extracted content.'),
        max_length=255, choices=CONTENT_MIME_TYPE_CHOICES)
    content_language = models.CharField('content language', blank=True,
        help_text=_('Language for the extracted content.'),
        max_length=255, choices=LANGUAGES)

    """ XPath enclosure extraction. """
    enclosure_xpath = models.CharField(_('enclosure XPath'), blank=True,
        help_text=_('XPath expression to find the enclosure href. Leave '
                    'blank to disable extraction.'), max_length=1024)
    enclosure_mime_type = models.CharField('enclosure MIME type', blank=True,
        help_text=_('MIME type to use for extracted enclosures.'),
        max_length=255)

    def save(self, *args, **kwargs):
        """ Make sure we fetch on first save action. """
        from .crawler import update_feed

        if not self.pk:
            new = True
        else:
            new = False

        # Make sure we save first
        super(Feed, self).save(*args, **kwargs)

        # If new, update the feed
        if new:
            update_feed(self)

    def __unicode__(self):
        """
        Unicode representation is title or URL if title has not been set.
        """
        if self.title:
            return self.title

        return self.url


class FeedEntry(models.Model):
    """
    Feed entries, largely modelled after feedparser's.

    Ref:
    http://packages.python.org/feedparser/reference-entry.html
    """

    class Meta:
        verbose_name = _('entry')
        verbose_name_plural = _('entries')
        ordering = ('-published', )

    feed = models.ForeignKey(Feed, related_name='entries')

    title = models.CharField(_('title'), max_length=1024)
    author = models.CharField(_('author'), max_length=255, blank=True)

    link = models.URLField(_('link'), db_index=True, max_length=330)
    # max_length = 330 seems to be the max. length MySQL can handle for index
    entry_id = models.CharField(_('remote entry id'), null=True,
        db_index=True, editable=False, max_length=255)

    published = models.DateTimeField(_('time published'))
    updated = models.DateTimeField(_('time updated'), null=True)

    summary = models.TextField(_('summary'), blank=True)

    def __unicode__(self):
        """
        Unicode representation is title or URL if title has not been set.
        """
        if self.title:
            return self.title

        return self.link


class FeedEnclosure(models.Model):
    """
    Feed enclosures, largely modelled after feedparser's.

    Ref:
    http://packages.python.org/feedparser/reference-entry-enclosures.html
    """
    class Meta:
        verbose_name = _('enclosure')
        verbose_name_plural = _('enclosures')

    entry = models.ForeignKey(FeedEntry, related_name='enclosures')

    href = models.URLField(_('href'), max_length=330)
    length = models.PositiveIntegerField(_('length'))
    mime_type = models.CharField(_('MIME type'), max_length=255)

    def __unicode__(self):
        """ Natural representation is href. """
        return self.href


class FeedContent(models.Model):
    """
    Feed content, largely modelled after feedparser's.

    Ref:
    http://packages.python.org/feedparser/reference-entry-content.html
    """
    class Meta:
        verbose_name = _('content')
        verbose_name_plural = _('content')

    entry = models.ForeignKey(FeedEntry, related_name='content')

    value = models.TextField(_('value'))
    mime_type = models.CharField(_('MIME type'), max_length=255)
    language = models.CharField(_('language'),
        max_length=16, blank=True, choices=LANGUAGES)

    def __unicode__(self):
        """ Natural representation is mime_type. """
        return self.mime_type
