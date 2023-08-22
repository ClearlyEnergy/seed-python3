# !/usr/bin/env python
# encoding: utf-8
"""
SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
See also https://github.com/seed-platform/seed/main/LICENSE.md
"""
from django.conf.urls import re_path

<<<<<<< HEAD
from django.conf.urls import url
from django.urls import path

from seed.views.main import (
    home,
)
=======
from seed.views.main import home
>>>>>>> seed-merge

from seed.views.properties import deep_list, deep_detail

urlpatterns = [
<<<<<<< HEAD
    path('deeplink-list/', deep_list, name='deeplink_list'),
    path('deeplink-detail/<int:pk>/', deep_detail, name='deeplink_details'),
    url(r'^$', home, name='home'),
=======
    re_path(r'^$', home, name='home'),
>>>>>>> seed-merge
]
