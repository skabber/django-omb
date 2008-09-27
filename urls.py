from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^follow/$', 'omb.views.follow', name="omb_follow"),
    url(r'^finish_follow/$', 'omb.views.finish_follow', name="omb_finish_follow"),
    url(r'^postnotice/$', 'omb.views.postnotice', name="omb_post_notice"),
    url(r'^updateprofile/$', 'omb.views.updateprofile', name="omb_update_profile"),
    url(r'^(?P<username>[\w]+)/xrds/$', 'omb.views.xrds', name="omb_xrds"),
)