from email import message
from hashlib import new
from logging import PlaceHolder
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Max
from django.contrib import messages
import validators as is_valid
from django.contrib.auth.decorators import login_required

from .models import Listing, Category, Bids, Comments, User

class CreateListing(forms.Form):
    title = forms.CharField(max_length=64, required=True)
    title.widget.attrs.update({'placeholder':'Enter title of your lot'})
    title.widget.attrs.update({'size':'50px'})
    
    desc = forms.CharField(label="Description", max_length=512, required=False, widget=forms.Textarea)
    desc.widget.attrs.update({'placeholder':'Enter description'})
    
    img = forms.URLField(label="Image link", required=False)
    img.widget.attrs.update({'placeholder':'Put here link for img'})
    img.widget.attrs.update({'size':'100px'})
    
    start_bid = forms.DecimalField(label="Start bid in $", max_digits=12, decimal_places=2, min_value=0.01, required=True)
    start_bid.widget.attrs.update({'placeholder':'Start bid in $'})
    start_bid.widget.attrs.update({'size':'100px'})
    
    category = forms.ModelChoiceField(queryset=Category.objects.filter().only('name'), required=True)


def print_list(request, listings, title):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    current_bids = []
    
    for listing in listings:
        current_bids.append(get_current_bid(listing.id))
    
    return render(request, "auctions/index.html", {
        "data": zip(listings, current_bids),
        "page_title": title,
        "watchlist_size": get_watchlist_sise(request)
    })

def get_current_bid(listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = listing.bidding_listing.all()
    if not bids:
        bid = listing.start_bid
    else:
        bids.order_by('bid')
        bid = bids.last().bid
    
    return bid

def get_current_bid_owner(listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = listing.bidding_listing.all()
    if not bids:
        bid_owner = listing.owner
    else:
        bids.order_by('bid')
        bid_owner = bids.last().user.username
    
    return bid_owner

def get_bids_count(listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = listing.bidding_listing.all()
    
    return bids.count()

def get_watchlist_sise(request):
    return request.user.watched_listings.count()


def index(request):
    return print_list(request, Listing.objects.all(), "Active Listings")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def category(request):
    categories = Category.objects.filter().only('name')
    
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "watchlist_size": get_watchlist_sise(request)
    })

@login_required
def category_res(request, categ):
    category = Category.objects.get(name=categ)
    return print_list(request, category.similar_listings.all(), ("Category: " + categ))

@login_required
def change_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.user in listing.watchers.all():
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)
        
    return HttpResponseRedirect(reverse("view_listing", args=[listing_id]))

@login_required
def watchlist(request):
    return print_list(request, request.user.watched_listings.all(), "Watchlist")

@login_required
def create_listing(request):
    
    categories = Category.objects.filter().only('name')
    
    if request.method == 'POST':
        form = CreateListing(request.POST)
        if form.is_valid():
        
            listing = Listing()
            
            listing.title = form.cleaned_data['title']
            listing.owner = request.user
            listing.desc = form.cleaned_data['desc']
            
            if is_valid.url(form.cleaned_data['img']):
                listing.img = form.cleaned_data['img']
            else:
                listing.img = "https://bit.ly/3rsWn9p"
            
            listing.start_bid = form.cleaned_data['start_bid']
            listing.category = form.cleaned_data['category']
            listing.is_active = True
            listing.save()

            messages.success(request, "Listing was created successfuly:)")
            return HttpResponseRedirect(reverse("view_listing", args=[listing.id]))
        
    return render(request, "auctions/create_listing.html", {
        "create_listing_form": CreateListing(),
        "categories": categories,
        "watchlist_size": get_watchlist_sise(request)
    })

@login_required
def view_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    
    in_watchlist = False
    if request.user in listing.watchers.all(): in_watchlist = True
        
    if not listing.is_active and request.user.username == get_current_bid_owner(listing_id):
        messages.success(request, "You won it:)")
    
    return render(request, "auctions/view_listing.html", {
        "listing": listing,
        "comments": listing.get_comments.all(),
        "viewer": request.user.username,
        "in_watchlist": in_watchlist,
        "listing_bid": get_current_bid(listing_id),
        "last_bid_owner": get_current_bid_owner(listing_id),
        "bids_num": get_bids_count(listing_id),
        "watchlist_size": get_watchlist_sise(request)
    })

@login_required
def add_comment(request, list_id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=list_id)
        content = request.POST.get("content")
        
        comment = Comments()
        comment.user = request.user
        comment.body = content
        comment.listing = listing
        comment.save()

    return HttpResponseRedirect(reverse("view_listing", args=[list_id]))

@login_required
def del_comment(request, list_id, comment_id):
    
    if request.method == 'POST':
        Comments.objects.filter(id=comment_id).delete()
        
    return HttpResponseRedirect(reverse("view_listing", args=[list_id]))

@login_required
def add_bid(request, list_id):
    if request.method == 'POST':
        listing = Listing.objects.get(id=list_id)
        bids = listing.bidding_listing.all()
        
        user_bid = request.POST.get("bid")
        cur_bid = get_current_bid(list_id)
            
        if int(user_bid) < int(cur_bid):
            messages.warning(request, 'Your bid have to be higher than the current one')
        else:
            new_bid = Bids()
            new_bid.listing = listing
            new_bid.user = request.user
            new_bid.bid = user_bid
            new_bid.save()
            messages.success(request, 'Your bid was adopted successfuly:)')
            
    return HttpResponseRedirect(reverse("view_listing", args=[list_id]))

@login_required
def change_status(request, listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(id=listing_id)
        listing.is_active = not(listing.is_active)
        listing.save()
    
    return HttpResponseRedirect(reverse("view_listing", args=[listing_id]))