import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.utils.translation import ugettext_lazy as _


class KeywordFilter(models.Model):
    """ A keyword-based filter to be used when importing feeds. """

    class Meta:
        verbose_name = _('keyword filter')
        verbose_name_plural = _('keyword filters')

    name = models.CharField(_('name'), max_length=255)
    keywords = models.TextField(_('description'))
    filter_title = models.BooleanField(_('filter title'))
    filter_summary = models.BooleanField(_('filter summary'))

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
    link = models.URLField(_('link'), blank=True)
    url = models.URLField(_('URL'))

    # feed_id = models.CharField(_('remote feed id'),
    #     unique=True, editable=False, max_length=255)

    updated = models.DateTimeField(_('time updated'),
            editable=False, null=True)

    description = models.TextField(_('description'), blank=True)
    active = models.BooleanField(_('active'), default=True, db_index=True)
    filters = models.ManyToManyField(KeywordFilter, null=True, blank=True)

    # Preserve some error data
    error_state = models.BooleanField(
        _('error'), help_text=_('Latest crawl yielded error.'),
        default=False, db_index=True)
    error_description = models.TextField(_('error description'),
        help_text=_('Description of latest crawl error.'), editable=False)
    error_date = models.DateTimeField(_('error date'), null=True,
        help_text=_('Latest time when an error was seen.'), editable=False)

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
    """ Feed entries. """

    class Meta:
        verbose_name = _('entry')
        verbose_name_plural = _('entries')
        ordering = ('-published', )

    feed = models.ForeignKey(Feed, related_name='entries')

    title = models.CharField(_('title'), max_length=1024)
    link = models.URLField(_('link'), db_index=True)
    entry_id = models.CharField(_('remote entry id'), null=True,
        db_index=True, editable=False, max_length=255)

    published = models.DateTimeField(_('time published'), editable=False)
    updated = models.DateTimeField(_('time updated'),
        editable=False, null=True)

    summary = models.TextField(_('summary'))

    def __unicode__(self):
        """
        Unicode representation is title or URL if title has not been set.
        """
        if self.title:
            return self.title

        return self.link

