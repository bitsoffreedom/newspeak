from django.conf.urls import patterns, url

from django.views.generic.base import RedirectView

from surlex.dj import surl

from .feeds import NewspeakRSSFeed, NewspeakAtomFeed


urlpatterns = patterns('',
    # surl(r'^$', SomeView.as_view(),
    #     name='newspeak_home'
    # ),)

    # Static redirect to the RSS feed, until we have a
    # page to show here.
    url(r'^$', RedirectView.as_view(
        url='/all/rss/', permanent=False
    )),

    url(r'^all/rss/$', NewspeakRSSFeed(), name='rss_all'),
    url(r'^all/atom/$', NewspeakAtomFeed(), name='atom_all'),
)
