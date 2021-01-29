# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2020, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""

from django.conf.urls import url
from django.urls import path

from seed.views.main import (
    home,
)

from seed.views.properties import deep_list, deep_detail

urlpatterns = [
    path('deeplink-list/', deep_list, name='deeplink_list'),
    path('deeplink-detail/<int:pk>/', deep_detail, name='deeplink_details'),
    url(r'^$', home, name='home'),
]
