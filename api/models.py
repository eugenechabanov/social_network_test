from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import requests
from random import randrange
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.CharField(max_length=128, blank=True)
    last_action = models.DateTimeField(auto_now=True)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + ':' + str(self.post) + ':' + str(self.value)

    # class Meta:
    #     unique_together = ("user", "post", "value")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile.objects.create(user=instance)
        p.image = get_portrait_image()
        p.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def get_portrait_image():
    headers = {        # very bad practice!!! don't you ever do this:
        'Authorization': 'Bearer v2/YWUyMmUtNzM3OWYtNzQ0NmMtMDI3ZDQtOTRlZDktZDdlZWYvMTE1NTE5NjczL2N1c3RvbWVyLzMvMnk3bXBlV3QxRm5qVXhCS0VwV25GRUF2dVpoSlNFSHJmOHJlejRUQ2UzenpyVDZ1ek15eUtQSnVpSUZKRzZNVGM2dWdkY2VKMjVVLWVrYVRfZmRkYzl5bDZVRXFPQWxtYjlXLTl2WC04bjR6dWVWak13a3NuSXVnaGtjcVNWVmhvZHZhdmlDRVo1Rk5VWVNvTjdwZ3VrTDNRU01BR2E5b3FRMElucTgwcmdGZ19CNEJfWHpjOVo4R0lBanhXRlJFMDhqbFR6ejJvcEQ3T3BoQzlxN0Fxdw'
    }
    query = 'man+closeup' if randrange(0, 1) else 'woman+closeup'
    url = 'https://api.shutterstock.com/v2/images/search?query={}'.format(query)
    r = requests.get(url, headers=headers, timeout=20)
    image_url = r.json()['data'][randrange(0, 20)]['assets']['large_thumb']['url']
    return image_url
