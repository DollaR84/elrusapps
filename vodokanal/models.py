from django.db import models

# Create your models here.

class News(models.Model):
    title = models.TextField()
    date = models.CharField(max_length=10)
    text = models.TextField()
    link_text = models.CharField(max_length=12)
    link_href = models.URLField()

    def __str__(self):
        return self.title
