#!/usr/bin/env python
#coding:utf-8
"""
  Author: --<SKB>
  Purpose: decorators
  Created: Monday 20 April 2015
"""
import traceback

from django.conf import settings
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import get_backends, login

from models import TProfile, SProfile

def login_megaforte_user(view_function):
    """
    Authenticates the user if url has api_key.
    """
    def wrap(request, *args, **kwargs):
        """
        Calling decorated function
        """
        try:
            if not has_api_key(request):
                print "Dose not have an api_key on request"
                raise Exception

            unique_key = request.GET.get('unique_key')
            if not unique_key:
                print "Dose not have an api_key on request"
            
            try:
                tprofile = TProfile.objects.get(api_key=unique_key)
                # Login after succecful register
                # Bypass `authenticate()` because we did't get the user password
                user = tprofile.user
                backend = get_backends()[0]
                user.backend = '%s.%s' % (backend.__module__, backend.__class__.__name__)
                login(request, user)
            except TProfile.DoesNotExist, TProfile.MultipleObjectsReturned:
                try:
                    sprofile = SProfile.objects.get(api_key=unique_key)
                    # Login after succecful register
                    # Bypass `authenticate()` because we did't get the user password
                    user = sprofile.user
                    backend = get_backends()[0]
                    user.backend = '%s.%s' % (backend.__module__, backend.__class__.__name__)
                    login(request, user)
                except SProfile.DoesNotExist, SProfile.MultipleObjectsReturned:
                    raise Exception
            print "logged in  "
            return view_function(request, *args, **kwargs)
        except Exception:
            traceback.print_exc()
            return view_function(request, *args, **kwargs)

    return wrap


def has_api_key(request):
    api_key = request.GET.get('api_key')
    if api_key:
        return api_key == settings.MEGAFORT_API_KEY
    return False
