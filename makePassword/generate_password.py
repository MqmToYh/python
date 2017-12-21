#!/usr/bin/python
#-*-coding:utf-8-*-
#生成密码

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'auth_apps.settings'

from django.contrib.auth.hashers import make_password, check_password

make_password('12456',salt='yzy-t86016776')
