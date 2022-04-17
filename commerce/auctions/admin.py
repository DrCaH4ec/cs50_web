from django.contrib import admin
from .models import Listing, Category, Bids, Comments, User

# Register your models here.
admin.site.register(Listing)

admin.site.register(Category)

admin.site.register(Bids)

admin.site.register(Comments)

admin.site.register(User)