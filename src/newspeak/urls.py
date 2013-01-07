from django.conf.urls import patterns, url

from surlex.dj import surl

from .feeds import NewspeakRSSFeed, NewspeakAtomFeed


urlpatterns = patterns('',
    # surl(r'^$', SomeView.as_view(),
    #     name='newspeak_home'
    # ),)
    url(r'^all/rss/$', NewspeakRSSFeed(), name='rss_all'),
    url(r'^all/atom/$', NewspeakAtomFeed(), name='atom_all'),
)
