from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *

from .forms import ListingForm, BidForm, CommentForm


def index(request):
    #Check active listings
    active_listings = [i for i in Listing.objects.all() if i.is_active == True]
    return render(request, "auctions/index.html", {
            "listings": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # Check if user has a watchlist
            try:
                watchlist = Watchlist.objects.get(user=user)
            except:
                watchlist = Watchlist(user=user)
                watchlist.save()

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


def createlisting(request):
    return render(request, "auctions/createlisting.html")


def savelisting(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]

            current_user = request.user

            listing = Listing(title=title,
                            description=description,
                            starting_bid=starting_bid,
                            image=image,
                            category=category.capitalize(),
                            listed_by=current_user)
            listing.save()

            # Create category if name is not None and DoesNotExist
            if category is not None:
                try:
                    Category.objects.get(name=category.capitalize())
                except Category.DoesNotExist:
                    category = Category(name=category.capitalize())
                    category.save()
    return redirect('index')


def listings(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    # Get current_bid
    current_bid = listing.starting_bid
    if (len(listing.bids.all()) > 0):
        current_bid = max([i.bid for i in listing.bids.all()])
    # If the auction is closed, get winner
    if (listing.is_active == False):
        bid = Bid.objects.get(bid=current_bid)
        winner = bid.listed_by
        return render(request, "auctions/closedlisting.html",{
            "listing": listing,
            "winner": winner,
            "comments": listing.comments.all()
        })
    # if user is the one who created the listing
    if (listing.listed_by == request.user):
        return render(request, "auctions/listing_owner.html", {
            "listing": listing,
            "bids_count": listing.bids.count(),
            "current_bid": current_bid,
            "comments": listing.comments.all()
        })
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids_count": listing.bids.count(),
        "current_bid": current_bid,
        "comments": listing.comments.all()
    })


@login_required
def watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user
    watchlist = Watchlist.objects.get(user=user)
    try:
        if listing in watchlist.listings.all():
            watchlist.listings.remove(listing)
        else:
            watchlist.listings.add(listing)
    except AttributeError:
        watchlist.listings.add(listing)
        watchlist.save()

    return redirect('listings', listing_id)


@login_required
def bid(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    current_user = request.user
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            # If The bid is as large as the starting bid,
            # and is greater than any other bids
            if(bid >= listing.starting_bid and
                all(bid > i.bid for i in listing.bids.all()) ):
                bid_object = Bid.objects.create(listing=listing,
                                                bid=bid,
                                                listed_by=current_user)
            else:
                return render(request, "auctions/error.html", {
                    "message": "The bid was not correct. It must be greater than current bid.",
                })
    return redirect('listings', listing_id)


@login_required
def closeauction(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.is_active = False
    listing.save()
    return redirect('index')


@login_required
def comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    current_user = request.user
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            Comment.objects.create(listing=listing,
                                comment=comment,
                                user=current_user)
    return redirect('listings', listing_id)


@login_required
def seewatchlist(request):
    watchlist = Watchlist.objects.get(user=request.user)
    listings = watchlist.listings.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html",{
        "categories": categories
    })


def category(request, category_name):
    listings = [listing for listing in Listing.objects.all()
                if listing.category == category_name]
    return render(request, "auctions/category.html",{
        "category": category_name,
        "listings": listings
    })
