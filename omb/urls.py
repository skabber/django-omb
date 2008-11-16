from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^follow/$', 'omb.views.follow', name="omb_follow"),
    url(r'^finish_follow/$', 'omb.views.finish_follow', name="omb_finish_follow"),
    url(r'^post_notice/$', 'omb.views.post_notice', name="omb_post_notice"),
    url(r'^update_profile/$', 'omb.views.updateprofile', name="omb_update_profile"),
    url(r'^(?P<username>[\w]+)/xrds/$', 'omb.views.xrds', name="omb_xrds"),
    
    url(r'^request_token/$', 'omb.views.omb_request_token', name="omb_request_token"),
    url(r'^authorize/$', 'omb.views.authorize', name="omb_user_authorization"),
)