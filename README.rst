============
 Django OMB
============

This is a re-usable Django application that adds support for the OpenMicroBlogging spec to your Django project.

--------------
 Dependencies 
--------------
 * pydataportability.xrds http://pypi.python.org/pypi/pydataportability.xrds/0.1dev-r43
 * django-oauth http://github.com/skabber/django-oauth/tree/master
 * openid http://pypi.python.org/pypi/python-openid/2.2.1

----------
 Settings
----------
OMB requires a couple new settings to be defined in your settings.py file.  The settings below is an example using the zwitscern app from Pinax.

 * OAUTH_AUTHORIZE_VIEW = 'omb.views.oauth_authorize'
 * OMB_FOLLOWING_MODULE = 'zwitschern.Following'
 * OMB_NOTICE_MODULE = 'zwitschern.Tweet'

Note that djangologging can interfere with the oauth and omb apps, so I also set 

 * LOGGING_OUTPUT_ENABLED = False

-------
 Pinax
-------
I have modified the zwitschern app from Pinax to be compatible with omb.  You can find all my changes to Pinax in this patch http://dpaste.com/hold/82366/

