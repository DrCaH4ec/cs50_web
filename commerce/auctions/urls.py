from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category", views.category, name="category"),
    path("category/<str:categ>", views.category_res, name="category_res"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/change/<int:listing_id>", views.change_watchlist, name="change_watchlist"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("add_comment/<int:list_id>", views.add_comment, name="add_comment"),
    path("del_comment/<int:list_id>/<int:comment_id>", views.del_comment, name="del_comment"),
    path("listings/<int:listing_id>", views.view_listing, name="view_listing"),
    path("listings/<int:listing_id>/change_status", views.change_status, name="change_status"),
    path("add_bid/<int:list_id>", views.add_bid, name="add_bid"),
]
