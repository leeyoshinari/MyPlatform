#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari
import re
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class AccessAuthMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        if re.search(settings.EXCLUDE_URL, request.path):
            return None

        if request.user.is_authenticated:
            return None
        else:
            return redirect('user:login')
