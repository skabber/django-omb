from django.contrib import admin
from omb.models import RemoteProfile

class RemoteProfileAdmin(admin.ModelAdmin):
    list_display = ('uri', 'post_notice_url', 'update_profile_url', 'created')

admin.site.register(RemoteProfile, RemoteProfileAdmin)