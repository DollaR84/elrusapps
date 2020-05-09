from django.db import models

# Create your models here.
import json



class Weather(models.Model):
    today = models.TextField()
    days = models.TextField()
    water = models.TextField()
    infoDaylight = models.TextField()
    warnings = models.TextField()
    description = models.TextField()

    def __str__(self):
        today = json.loads(self.today)
        return 'Today: {} {} {}'.format(today['date'], today['month'], today['year'])


class UpdateDay(models.Model):
    day = models.TextField()

    def __str__(self):
        return self.day
