from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^follow/$', 'omb.views.follow'),
    (r'^finish_follow/$', 'omb.views.finish_follow'),
    (r'^postnotice/$', 'omb.views.postnotice'),
    (r'^updateprofile/$', 'omb.views.updateprofile'),
)