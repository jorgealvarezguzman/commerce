from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64)
    starting_bid = models.FloatField()
    description = models.CharField(max_length=256, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.CharField(max_length=2550, blank=True)
    category = models.CharField(max_length=64, blank=True)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE)


class Bid(models.Model):
    listings = models.ManyToManyField(Listing, related_name="bids")
    bid = models.FloatField()


class Comment(models.Model):
    listings = models.ManyToManyField(Listing, related_name="comments")
    comment = models.CharField(max_length=512)
