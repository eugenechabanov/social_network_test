from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import requests
from random import randrange


class Post(models.Model):
    content = models.TextField(max_length=2000)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    number_of_likes = models.IntegerField(default=0)
    image = models.CharField(null=True, blank=True, max_length=128)

    @property
    def get_unique_image(self):
        headers = {
            'Host': 'www.shutterstock.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
        }
        while True:
            # sufficient url to consider appearing images random and unique
            url = 'https://www.shutterstock.com/studioapi/images/15373{}'.format(randrange(10000, 99999))
            r = requests.get(url, headers=headers, timeout=20)
            # some urls (image ids) are 404, so we wait for a 200 hit, usually less than 5 tries
            if r.status_code == 200:
                break
        image_url = r.json()['data']['attributes']['src']
        return image_url

    def save(self, *args, **kwargs):
        """ if we create a new model - get a unique image for it, if we edit existing, leave current image """
        if self.image is None:
            self.image = self.get_unique_image
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return 'Id: {}. {}...'.format(self.id, self.content[:40])


