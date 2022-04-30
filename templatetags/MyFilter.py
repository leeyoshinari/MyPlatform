#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari
from django.template import Library


register = Library()


@register.filter
def get_list(v1, v2):
    try:
        return v1[v2]
    except:
        return None