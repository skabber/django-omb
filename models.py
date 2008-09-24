from django.db import models

class RemoteProfile(models.Model):
    username = models.CharField(max_length=30)
    uri = models.CharField(unique=True, max_length=600)
    url = models.URLField(verify_exists=False)
    post_notice_url = models.CharField(max_length=600)
    update_profile_url = models.CharField(max_length=600)
    created = models.DateTimeField(auto_now_add=True)

