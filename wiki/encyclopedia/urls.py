from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search_entry, name="search_entry"),
    path("add", views.add_entry, name="add_entry"),
    path("random_page", views.random_page, name="random_page"),
    path("wiki/<str:title>", views.show_entry, name="show_entry"),
    path("<str:title>/edit_entry", views.edit_entry, name="edit_entry")
]
