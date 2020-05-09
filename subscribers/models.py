from django.db import models

# Create your models here.

class Subscribers(models.Model):
    subscriber = models.EmailField()
    vodokanal = models.BooleanField(default=False)
    weather = models.BooleanField(default=False)

    def __str__(self):
        return self.subscriber + ' vodokanal: ' + str(self.vodokanal) + ' weather: ' + str(self.weather)
