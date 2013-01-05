from django.conf.urls import patterns

from surlex.dj import surl

from .feeds import NewspeakRSSFeed, NewspeakAtomFeed


urlpatterns = patterns('',
    # surl(r'^$', SomeView.as_view(),
    #     name='newspeak_home'
    # ),)
    (r'^all/rss/$', NewspeakRSSFeed()),
    (r'^all/atom/$', NewspeakAtomFeed()),
)
