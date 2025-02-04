from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("savelisting", views.savelisting, name="savelisting"),
    path("listings/<int:listing_id>", views.listings, name="listings"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("closeauction/<int:listing_id>", views.closeauction, name="closeauction"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("seewatchlist", views.seewatchlist, name="seewatchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_name>", views.category, name="category")
]
