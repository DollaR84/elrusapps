"""weather URL Configuration

"""

from django.conf.urls import url

from . import views

app_name = 'weather'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
