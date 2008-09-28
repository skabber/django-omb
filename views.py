from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from omb.forms import RemoteSubscribeForm, AuthorizeForm
from omb import oauthUtils, oauthConsumer, OAUTH_REQUEST, OAUTH_ACCESS, OMB_POST_NOTICE, OMB_UPDATE_PROFILE, OAUTH_AUTHORIZE
from omb.models import RemoteProfile

from oauth_provider.oauth import OAuthRequest, OAuthServer, OAuthSignatureMethod_HMAC_SHA1
from oauth_provider.stores import DataStore
from oauth_provider.views import request_token, user_authorization
from oauth_provider.models import Consumer

import urllib
import logging

def follow(request):
    if request.method == "GET":
        form = RemoteSubscribeForm(initial={'username': request.GET.get('username')})
    else:
        current_site = Site.objects.get_current()
        form = RemoteSubscribeForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            omb = oauthUtils.getServices(form.cleaned_data['profile_url'])
            token = oauthConsumer.requestToken(omb)
            oauthRequest = oauthConsumer.requestAuthorization(token, omb[OAUTH_AUTHORIZE].uris[0].uri, omb[OAUTH_REQUEST].localid.text, user)
            # store a bunch of stuff in the session varioable oauth_authorization_request
            omb_session = {
                'listenee': user.username,
                'listener': omb[OAUTH_REQUEST].localid.text,
                'token': token.key,
                'secret': token.secret,
                'access_token_url': omb[OAUTH_ACCESS].uris[0].uri,
                'post_notice_url': omb[OMB_POST_NOTICE].uris[0].uri,
                'update_profile_url': omb[OMB_UPDATE_PROFILE].uris[0].uri,
            }
            request.session['oauth_authorization_request'] = omb_session
            return HttpResponseRedirect(oauthRequest.to_url())            
    return render_to_response('omb/remote_subscribe.html', {'form': form})

def finish_follow(request):
    omb_session = request.session['oauth_authorization_request']
    oauth_request = OAuthRequest.from_request(request.method, request.build_absolute_uri(), headers=request.META)
    accessToken = oauthConsumer.requestAccessToken(omb_session, oauth_request)
    try:
        remote_profile = RemoteProfile.objects.get(uri=omb_session["listener"])
    except:
        remote_profile = RemoteProfile()
        remote_profile.username = oauth_request.get_parameter("omb_listener_nickname")
        remote_profile.uri = omb_session["listener"]
        remote_profile.url = oauth_request.get_parameter('omb_listener_profile')
        remote_profile.post_notice_url = omb_session["post_notice_url"]
        remote_profile.update_profile_url = omb_session["update_profile_url"]
        remote_profile.token = accessToken.key
        remote_profile.secret = accessToken.secret
        remote_profile.save()
    
    user = User.objects.get(username=omb_session['listenee'])
    
    # TODO wrap this in a try catch
    app_label, model_name = settings.OMB_FOLLOWING_MODULE.split('.')
    model = models.get_model(app_label, model_name)
    
    following = model()
    following.followed_content_object = user
    following.follower_content_object = remote_profile
    following.save()
    return HttpResponseRedirect(user.get_absolute_url())
    

def post_notice(request):
    current_site = Site.objects.get_current()
    signature_methods = {
        OAuthSignatureMethod_HMAC_SHA1().get_name(): OAuthSignatureMethod_HMAC_SHA1
    }
    oauth_req = OAuthRequest.from_request(request.method, request.build_absolute_uri(), headers=request.META)
    if not oauth_req:
        return HttpResponse("Not a OAuthRequest")
    else:
        oauth_server = OAuthServer(data_store=DataStore(oauth_req), signature_methods=signature_methods)
        oauth_server.verify_request(oauth_request)
        # TOOD Refactor this into something like omb.post_notice
        version = oauth_req.get_parameter('omb_version')
        if version != omb.OMB_VERSION_01:
            return HttpResponse("Unsupported OMB version")
        listenee = oauth_req.get_parameter('omb_listenee')
        remote_profile = RemoteProfile.objects.get(uri=listenee)
        if not remote_profile:
            return HttpResposne("Profile unknown")
        subscription = Subscription.objects.get(token=oauth_req.get_parameter('token'))
        if not subscription:
            return HttpResponse("No such subscription")
        content = oauth_req.get_parameter('omb_notice_content')
        if not content or len(content) > 140:
            return HttpResponse("Invalid notice content")
        notice_uri = oauth_req.get_parameter('omb_notice')
        # TODO Validate this uri exists
            # Invalid notice uri
        notice_url = oauth_uri.get_parameter("omb_notice_url")
        # TODO Validate this url 
            # Invalid notice url
        try:
            Notice.objects.get(uri=notice_uri)
        except: # TODO catch the real exception
            notice = Notice.objects.create(profile=remote_profile, content=content, )
            # TODO this is bad, do this better
            # TODO add the notice.source = "omb"
            # TODO add notice.is_local=False
            notice.uri = "%s/notice/%s" % (current_site.domain, notice.id)
            notice.save()
            # Broadcast to remote subscribers ===================================
            subscriptions = Subscription.objects.filter(subscribed=notice.profile)
            for sub in subcriptions:
                rp = RemoteProfile.objects.get(id=sub.subscriber.id)
                omb.post_notice_keys(notice, rp.postnoticeurl, sub.token, sub.secret)
                
            
        return HttpResponse("omb_version=%s" % omb.OMB_VERSION_01)

def updateprofile(request):
    return HttpResponse("update profile")

def xrds(request, username):
    current_site = Site.objects.get_current()
    user = get_object_or_404(User, username=username)
    return render_to_response("xrds.xml", {"site_domain": current_site.domain}, mimetype="text/xml", context_instance=RequestContext(request))

def omb_request_token(request):
    consumer_key = request.REQUEST.get("oauth_consumer_key")
    logging.debug("consumer key: %s" % consumer_key)
    try:
	logging.debug("See if we already have a key for: %s" % consumer_key)
        Consumer.objects.get(name=consumer_key, key=consumer_key)
        logging.debug("We already have the consumer key")
    except ObjectDoesNotExist:
	logging.debug("We don't create a new one")
        Consumer.objects.create(name=consumer_key, key=consumer_key)
        logging.debug("Create a new consumer key")
    logging.debug("did we get here?")
    response = request_token(request)
    logging.debug(response)
    return response

def authorize(request):
    if request.method == "GET":
        return user_authorization(request)
    else:
        response = user_authorization(request)
        if type(response) == HttpResponseRedirect:
            # Add on the necessary omb parameters
            location = response['Location']
            params = {}
            if location.find("?") > -1:
                location += "&%s" % urllib.urlencode(params)
            else:
                location += "?%s" % urllib.urlencode(params)
        return response

def oauth_authorize(request, token, callback, params):
    if request.method == "GET":
        form = AuthorizeForm({
            'token': token.key,
        })
        context_vars = {
            "form": form,
            "username": request.GET.get("omb_listenee_nickname"),
            "full_name": request.GET.get("omb_listenee_fullname", ""),
            "bio": request.GET.get("omb_listenee_bio", ""),
            "location": request.GET.get("omb_listenee_location", ""),
            "avatar": request.GET.get("omb_listenee_avatar", ""),
            "query_string": request.META.get("QUERY_STRING")
        }
    else:
        form = AuthorizeForm(request.POST)
        print request.POST
    return render_to_response("omb/authorize.html", context_vars, context_instance=RequestContext(request))
