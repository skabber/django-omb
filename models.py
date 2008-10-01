from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse
from omb import oauthConsumer

notice_app_label, notice_model_name = settings.OMB_NOTICE_MODULE.split('.')
noticeModel = models.get_model(notice_app_label, notice_model_name)

following_app_label, following_module_name = settings.OMB_FOLLOWING_MODULE.split('.')
followingModel = models.get_model(following_app_label, following_module_name)

class RemoteProfile(models.Model):
    username = models.CharField(max_length=30)
    uri = models.CharField(unique=True, max_length=600)
    url = models.URLField(verify_exists=False)
    avatar = models.CharField(max_length=300, blank=True)
    
    post_notice_url = models.CharField(max_length=600, blank=True)
    update_profile_url = models.CharField(max_length=600, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=300, blank=True)
    secret = models.CharField(max_length=300, blank=True)

def send_notice_to_remote_followers(sender, instance, created, **kwargs):
    user = instance.sender
    remote_followers = followingModel.objects.filter(followed_object_id=user.id, follower_content_type=ContentType.objects.get_for_model(RemoteProfile))
    for follower in remote_followers:
        remote_profile = follower.follower_content_object
        print "Sending tweet to %s at %s" % (remote_profile.username, remote_profile.url)
        notice_url = reverse('single_tweet', args=[instance.id])
        oauthConsumer.postNotice(remote_profile.token, remote_profile.secret, remote_profile.post_notice_url, instance.text, notice_url, user)

post_save.connect(send_notice_to_remote_followers, sender=noticeModel)