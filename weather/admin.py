from django.contrib import admin

# Register your models here.

from .models import Weather
from .models import UpdateDay


admin.site.register(Weather)
admin.site.register(UpdateDay)
