from django.urls import path

from .views import *

urlpatterns = [
    path("movies/", MovieList.as_view(), name="movies"),
    path("movie/<uuid:id>/", MovieOperations.as_view(), name="movie"),
]