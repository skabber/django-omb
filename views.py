from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from omb.forms import RemoteSubscribeForm, AuthorizeForm
from omb import oauthUtils, oauthConsumer, OAUTH_REQUEST, OAUTH_ACCESS, OMB_POST_NOTICE, OMB_UPDATE_PROFILE, OAUTH_AUTHORIZE, OMB_VERSION_01
from omb.models import RemoteProfile

from oauth.oauth import OAuthRequest, OAuthServer, OAuthSignatureMethod_HMAC_SHA1, OAuthSignatureMethod_PLAINTEXT, OAuthError
from oauth_provider.stores import DataStore
from oauth_provider.views import request_token, user_authorization
from oauth_provider.models import Consumer

import urllib

signature_methods = {
    OAuthSignatureMethod_HMAC_SHA1().get_name(): OAuthSignatureMethod_HMAC_SHA1(),
    OAuthSignatureMethod_PLAINTEXT().get_name(): OAuthSignatureMethod_PLAINTEXT()
}

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
    return render_to_response('remote_subscribe.html', {'form': form})

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
        remote_profile.avatar = oauth_request.get_parameter('omb_listener_avatar')
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
    oauth_req = OAuthRequest.from_request(request.method, request.build_absolute_uri(), headers=request.META, parameters=request.POST.copy())
    if not oauth_req:
        return HttpResponse("Not a OAuthRequest", mimetype="text/plain")
    else:
        oauth_server = OAuthServer(data_store=DataStore(oauth_req), signature_methods=signature_methods)
        oauth_server.verify_request(oauth_req)
        # TOOD Refactor this into something like omb.post_notice
        version = oauth_req.get_parameter('omb_version')
        if version != OMB_VERSION_01:
            return HttpResponse("Unsupported OMB version", mimetype="text/plain")
        listenee = oauth_req.get_parameter('omb_listenee')
        try:
            remote_profile = RemoteProfile.objects.get(uri=listenee)
        except ObjectDoesNotExist:
            return HttpResponse("Profile unknown", mimetype="text/plain")
        content = oauth_req.get_parameter('omb_notice_content')
        if not content or len(content) > 140:
            return HttpResponse("Invalid notice content", mimetype="text/plain")
        notice_uri = oauth_req.get_parameter('omb_notice')
        notice_url = oauth_req.get_parameter("omb_notice_url")

        notice_app_label, notice_model_name = settings.OMB_NOTICE_MODULE.split('.')
        noticeModel = models.get_model(notice_app_label, notice_model_name)
        notice = noticeModel()
        notice.sender = remote_profile
        notice.text = content
        notice.save()
            
        return HttpResponse("omb_version=%s" % OMB_VERSION_01, mimetype="text/plain")

def updateprofile(request):
    oauth_req = OAuthRequest.from_request(request.method, request.build_absolute_uri(), headers=request.META, parameters=request.POST.copy())
    return HttpResponse("update profile", mimetype="text/plain")
    if not oauth_req:
        return HttpResponse("Not a OAuthRequest", mimetype="text/plain")
    else:
        oauth_server = OAuthServer(data_store=DataStore(oauth_req), signature_methods=signature_methods)
        oauth_server.verify_request(oauth_req)
        # TOOD Refactor this into something like omb.update_profile
        omb_version = oauth_req.get_parameter('omb_version')
        if omb_version != OMB_VERSION_01:
            return HttpResponse("Unsupported OMB version", mimetype="text/plain")
        omb_listenee = oauth_req.get_parameter('omb_listenee')
        try:
            remote_profile = RemoteProfile.objects.get(uri=omb_listenee)
            omb_listenee_profile = _get_oauth_param(oauth_req, 'omb_listenee_profile')
            if omb_listenee_profile != None:
                remote_profile.url = omb_listenee_profile
            omb_listenee_nickname = _get_oauth_param(oauth_req, 'omb_listenee_nickname')
            if omb_listenee_nickname != None:
                remote_profile.username = omb_listenee_nickname
            omb_listenee_license = _get_oauth_param(oauth_req, 'omb_listenee_license')
            if omb_listenee_license != None:
                remote_profile.license = omb_listenee_license
            omb_listenee_fullname = _get_oauth_param(oauth_req, 'omb_listenee_fullname')
            if omb_listenee_fullname != None:
                remote_profile.fullname = omb_listenee_fullname
            omb_listenee_homepage = _get_oauth_param(oauth_req, 'omb_listenee_homepage')
            if omb_listenee_homepage != None:
                remote_profile.homepage = omb_listenee_homepage
            omb_listenee_bio = _get_oauth_param(oauth_req, 'omb_listenee_bio')
            if omb_listenee_bio != None:
                remote_profile.bio = omb_listenee_bio
            omb_listenee_location = _get_oauth_param(oauth_req, 'omb_listenee_location')
            if omb_listenee_location != None:
                remote_profile.location = omb_listenee_location
            omb_listenee_avatar = _get_oauth_param(oauth_req, 'omb_listenee_avatar')
            if omb_listenee_avatar != None:
                remote_profile.avatar = omb_listenee_avatar
            
            remote_profile.save()
            return HttpResponse("omb_version=%s" % OMB_VERSION_01, mimetype="text/plain")
        except ObjectDoesNotExist:
            return HttpResponse("Profile unknown", mimetype="text/plain")

def _get_oauth_param(oauth_req, field_name):
    try:
        return oauth_req.get_parameter(field_name)
    except OAuthError:
        return None
    
def xrds(request, username):
    current_site = Site.objects.get_current()
    other_user = get_object_or_404(User, username=username)
    return render_to_response("xrds.xml", {"site_domain": current_site.domain, "other_user": other_user}, mimetype="text/xml", context_instance=RequestContext(request))

def omb_request_token(request):
    consumer_key = request.REQUEST.get("oauth_consumer_key")
    try:
        Consumer.objects.get(name=consumer_key, key=consumer_key)
    except ObjectDoesNotExist:
        Consumer.objects.create(name=consumer_key, key=consumer_key)
    response = request_token(request)
    return response

def authorize(request):
    if request.method == "GET":
        return user_authorization(request)
    else:
        current_site = Site.objects.get_current()
        user_profile_url = "http://%s%s" % (current_site.domain, reverse('profile_detail', args=[request.user.username]))
        response = user_authorization(request)
        if type(response) == HttpResponseRedirect: # TODO Check that it was 200 a success etc.
            # get the RemoteProfile for the user we are going to follow
            try:
                remote_profile = RemoteProfile.objects.get(uri=request.GET.get("omb_listenee"))
            except:
                remote_profile = RemoteProfile()
                remote_profile.username = request.GET.get("omb_listenee_nickname")
                remote_profile.uri = request.GET.get("omb_listenee")
                remote_profile.url = request.GET.get("omb_listenee_profile")
                remote_profile.license = request.GET.get("omb_listenee_license")
                remote_profile.fullname = request.GET.get("omb_listenee_fullname")
                remote_profile.homepage = request.GET.get("omb_listenee_homepage")
                remote_profile.bio = request.GET.get("omb_listenee_bio")
                remote_profile.location = request.GET.get("omb_listenee_location")
                remote_profile.avatar = request.GET.get("omb_listenee_avatar")
                # TODO get the post_notice_url and the update_profile_url by getting the XRDS file from the omb_listenee_profile
                #remote_profile.post_notice_url = ""
                #remote_profile.update_profile_url = ""
                remote_profile.save()
            # TODO wrap this in a try catch
            app_label, model_name = settings.OMB_FOLLOWING_MODULE.split('.')
            following_model = models.get_model(app_label, model_name)
            # create the following between the user and the remote profile
            following = following_model()
            following.followed_content_object = remote_profile
            following.follower_content_object = request.user
            following.save()
            
            # Add on the necessary omb parameters
            location = response['Location']
            params = {
                "omb_version": "http://openmicroblogging.org/protocol/0.1",
                "omb_listener_nickname": request.user.username,
                "omb_listener_profile": user_profile_url,
            }
            if location.find("?") > -1:
                location += "&%s" % urllib.urlencode(params)
            else:
                location += "?%s" % urllib.urlencode(params)
            response['Location'] = location
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
    return render_to_response("authorize.html", context_vars, context_instance=RequestContext(request))
