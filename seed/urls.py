# !/usr/bin/env python
# encoding: utf-8
"""
SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
See also https://github.com/seed-platform/seed/main/LICENSE.md
"""
from django.conf.urls import re_path

from seed.views.main import home

from seed.views.v3.properties import deep_list, deep_detail

urlpatterns = [
    re_path('deeplink-list/', deep_list, name='deeplink_list'),
    re_path('deeplink-detail/<int:pk>/', deep_detail, name='deeplink_details'),
    re_path(r'^$', home, name='home'),
]
