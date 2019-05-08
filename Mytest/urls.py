# coding:utf-8

from . import views
from django.conf.urls import url

urlpatterns = [
    url(r"^translate/$",views.translate,name='translate'),
    url(r'^translate_char/$',views.translate_char,name='translate_char')
]
