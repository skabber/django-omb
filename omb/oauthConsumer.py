from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from omb import OMB_VERSION_01, OAUTH_REQUEST, OAUTH_ACCESS, OMB_POST_NOTICE, OMB_UPDATE_PROFILE
from oauth.oauth import OAuthConsumer, OAuthRequest, OAuthSignatureMethod_HMAC_SHA1, OAuthToken
import urlparse, urllib

def requestToken(omb):
    current_site = Site.objects.get_current()
    url = urlparse.urlparse(omb[OAUTH_REQUEST].uris[0].uri)
    params = {}
    if url[4] != '':
        # We need to copy over the query string params for sites like laconica
        params.update(dict([part.split('=') for part in url[4].split('&')]))
    params['omb_version'] = OMB_VERSION_01
    params['omb_listener'] = omb[OAUTH_REQUEST].localid.text
    consumer = OAuthConsumer(current_site.domain, "")
    req = OAuthRequest().from_consumer_and_token(consumer, http_url=url.geturl(), parameters=params, http_method="POST")
    req.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
    f = urllib.urlopen(url.geturl(), req.to_postdata())
    data = f.read()
    requestToken = OAuthToken.from_string(data)
    return requestToken

def requestAuthorization(token, url, listener, user):
    current_site = Site.objects.get_current()
    user_profile_url = "%s%s" % (current_site.domain, reverse('profile_detail', args=[user.username]))
    profile = user.get_profile()
    url = urlparse.urlparse(url)
    params = {}
    if url[4] != '':
        # We need to copy over the query string params for sites like laconica
        params.update(dict([part.split('=') for part in url[4].split('&')]))
    params['omb_version'] = OMB_VERSION_01
    params['omb_listener'] = listener
    params['omb_listenee'] = "http://%s" % user_profile_url
    params['omb_listenee_profile'] = "http://%s" % user_profile_url
    params['omb_listenee_nickname'] = user.username
    params['omb_listenee_license'] = 'http://%s/license/' % current_site.domain # TODO link to the real license
    params['omb_listenee_fullname'] = "%s %s" % (user.first_name, user.last_name)
    params['omb_listenee_homepage'] = "" # TOOD Pinax doesn't have this
    params['omb_listenee_bio'] = profile.about
    params['omb_listenee_location'] = profile.location
    params['omb_listenee_avatar'] = '' # TODO get the avatar url
    params['oauth_callback'] = 'http://%s/omb/finish_follow/' % current_site.domain
    consumer = OAuthConsumer(current_site.domain, "")
    oauth_request = OAuthRequest().from_consumer_and_token(consumer, http_url=url.geturl(), parameters=params, http_method="GET", token=token)
    oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
    return oauth_request

def requestAccessToken(omb_session, oauth_request):
    current_site = Site.objects.get_current()
    token = OAuthToken(omb_session["token"], omb_session["secret"])
    url = urlparse.urlparse(omb_session["access_token_url"])
    params = {}
    if url[4] != '':
        # We need to copy over the query string params for sites like laconica
        params.update(dict([part.split('=') for part in url[4].split('&')]))
    params['omb_version'] = OMB_VERSION_01
    consumer = OAuthConsumer(current_site.domain, "")
    req = OAuthRequest().from_consumer_and_token(consumer, token=token, http_url=url.geturl(), parameters=params, http_method="POST")
    req.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, token)
    f = urllib.urlopen(url.geturl(), req.to_postdata())
    data = f.read()
    accessToken = OAuthToken.from_string(data)
    return accessToken

def postNotice(token, secret, post_notice_url, notice_content, notice_url, user):
    current_site = Site.objects.get_current()
    user_profile_url = "%s%s" % (current_site.domain, reverse('profile_detail', args=[user.username]))
    oauthToken = OAuthToken(token, secret)
    url = urlparse.urlparse(post_notice_url)
    params = {}
    if url[4] != '':
        # We need to copy over the query string params for sites like laconica
        params.update(dict([part.split('=') for part in url[4].split('&')]))
    params['omb_version'] = OMB_VERSION_01
    params['omb_listenee'] = user_profile_url
    params['omb_notice'] = "%s%s" % (current_site.domain, notice_url)
    params['omb_notice_content'] = notice_content
    params['omb_notice_url'] = "%s%s" % (current_site.domain, notice_url)
    params['omb_notice_license'] = '%s/license/' % current_site.domain # TODO link to the real license
    
    consumer = OAuthConsumer(current_site.domain, "")
    req = OAuthRequest().from_consumer_and_token(consumer, token=oauthToken, http_url=url.geturl(), parameters=params, http_method="POST")
    req.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, oauthToken)
    f = urllib.urlopen(url.geturl(), req.to_postdata())
    data = f.read()
    # TODO log failures

def updateProfile(token, secret, update_profile_url, profile):
    current_site = Site.objects.get_current()
    user_profile_url = "%s%s" % (current_site.domain, reverse('profile_detail', args=[profile.user.username]))
    oauthToken = OAuthToken(token, secret)
    url = urlparse.urlparse(update_profile_url)
    params = {}
    if url[4] != '':
        # We need to copy over the query string params for sites like laconica
        params.update(dict([part.split('=') for part in url[4].split('&')]))
    params['omb_version'] = OMB_VERSION_01
    params['omb_listenee'] = user_profile_url
    params['omb_listenee_profile'] = user_profile_url
    params['omb_listenee_nickname'] = profile.username
    params['omb_listenee_license'] = '%s/license/' % current_site.domain # TODO link to the real license
    params['omb_listenee_fullname'] = profile.name
    params['omb_listenee_homepage'] = profile.website
    params['omb_listenee_bio'] = profile.about
    params['omb_listenee_location'] = profile.location
    #params['omb_listenee_avatar'] = TODO get the gravatar of the user
    
    consumer = OAuthConsumer(current_site.domain, "")
    req = OAuthRequest().from_consumer_and_token(consumer, token=oauthToken, http_url=url.geturl(), parameters=params, http_method="POST")
    req.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, oauthToken)
    f = urllib.urlopen(url.geturl(), req.to_postdata())
    data = f.read()
    # TODO log failures