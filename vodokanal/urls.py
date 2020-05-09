"""vodokanal URL Configuration

"""

from django.conf.urls import url

from . import views

app_name = 'vodokanal'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
