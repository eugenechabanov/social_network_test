from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Post(models.Model):
    content = models.TextField(max_length=2000)
    image = models.ImageField(height_field=400, width_field=600, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    number_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.content[:30]
