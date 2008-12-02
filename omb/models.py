from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from omb import oauthConsumer

notice_app_label, notice_model_name = settings.OMB_NOTICE_MODULE.split('.')
noticeModel = models.get_model(notice_app_label, notice_model_name)

following_app_label, following_module_name = settings.OMB_FOLLOWING_MODULE.split('.')
followingModel = models.get_model(following_app_label, following_module_name)

profile_app_label, profile_model_name = settings.AUTH_PROFILE_MODULE.split('.')
profileModel = models.get_model(profile_app_label, profile_model_name)

class RemoteProfile(models.Model):
    username = models.CharField(_('username'), max_length=30)
    uri = models.CharField(_('uri'), unique=True, max_length=600)
    url = models.URLField(_('URL'), verify_exists=False)
    license = models.URLField(_('license'), verify_exists=False, blank=True)
    fullname = models.CharField(_('full name'), max_length=100, blank=True)
    homepage = models.URLField(_('homepage'), verify_exists=False, blank=True)
    bio = models.TextField(_('bio'), blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    avatar = models.CharField(_('avatar'), max_length=300, blank=True)

    post_notice_url = models.CharField(_('post notice URL'), max_length=600, blank=True)
    update_profile_url = models.CharField(_('update profile URL'), max_length=600, blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    token = models.CharField(_('token'), max_length=300, blank=True)
    secret = models.CharField(_('secret'), max_length=300, blank=True)

    class Meta:
        verbose_name = _('remote profile')
        verbose_name_plural = _('remote profiles')

def send_notice_to_remote_followers(sender, instance, created, **kwargs):
    user = instance.sender
    remote_followers = followingModel.objects.filter(followed_object_id=user.id, follower_content_type=ContentType.objects.get_for_model(RemoteProfile))
    for follower in remote_followers:
        remote_profile = follower.follower_content_object
        notice_url = reverse('single_tweet', args=[instance.id])
        oauthConsumer.postNotice(remote_profile.token, remote_profile.secret, remote_profile.post_notice_url, instance.text, notice_url, user)

def update_profile_to_remote_followers(sender, instance, created, **kwargs):
    user = instance.user
    remote_followers = followingModel.objects.filter(followed_object_id=user.id, follower_content_type=ContentType.objects.get_for_model(RemoteProfile))
    for follower in remote_followers:
        remote_profile = follower.follower_content_object
        oauthConsumer.updateProfile(remote_profile.token, remote_profile.secret, remote_profile.update_profile_url, instance)

post_save.connect(send_notice_to_remote_followers, sender=noticeModel)
post_save.connect(update_profile_to_remote_followers, sender=profileModel)