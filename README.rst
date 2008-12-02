============
 Django OMB
============

This is a re-usable Django application that adds support for the OpenMicroBlogging spec to your Django project.  For more info on OpenMicroBlogging visit http://openmicroblogging.org/

--------------
 Dependencies 
--------------
 * django.contrib.auth http://docs.djangoproject.com/en/dev/topics/auth/#topics-auth
 * django.contrib.sites http://docs.djangoproject.com/en/dev/ref/contrib/sites/
 * pydataportability.xrds http://pypi.python.org/pypi/pydataportability.xrds/0.1dev-r43
 * django-oauth http://www.bitbucket.org/david/django-oauth/overview/
 * openid http://pypi.python.org/pypi/python-openid/2.2.1

----------
 Settings
----------
OMB requires a couple new settings to be defined in your settings.py file.  The settings below is an example using the zwitscern app from Pinax.

 * OAUTH_AUTHORIZE_VIEW = 'omb.views.oauth_authorize'
 * OMB_FOLLOWING_MODULE = 'zwitschern.Following'
 * OMB_NOTICE_MODULE = 'zwitschern.Tweet'
 * AUTH_PROFILE_MODULE = 'profiles.Profile'

-------
 Pinax
-------
I have modified the zwitschern app from Pinax to be compatible with omb.  You can find all my changes to Pinax in this patch http://dpaste.com/hold/82366/

