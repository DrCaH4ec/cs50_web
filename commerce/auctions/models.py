from csv import unregister_dialect
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)

class Category(models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, primary_key=True)
    def __str__(self):
        return f"{self.name}"
        

class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    owner = models.ForeignKey(User, on_delete = models.CASCADE, related_name="user_data")
    desc = models.TextField(max_length=512, blank=True)
    img = models.CharField(max_length=256, default="https://bit.ly/3uAPmp5", blank=True)
    start_bid = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="similar_listings")
    publ_date = models.DateTimeField(auto_now_add=True)
    watchers = models.ManyToManyField(User, blank=True, related_name="watched_listings")
    is_active = models.BooleanField()
    
    def __str__(self):
        return f"{self.title}"

class Bids(models.Model):
    id = models.AutoField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name="bidding_listing")
    user = models.ForeignKey(User,on_delete = models.CASCADE, related_name="bidding_user")
    bid = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commited_user")
    body = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="get_comments")
    date_added = models.DateTimeField(auto_now_add=True)