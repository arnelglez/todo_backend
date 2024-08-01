from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated

from .models import Movie
from .serializers import MovieSerializer
from .mixins import MixinsList, MixinOperations


class MovieList(APIView, MixinsList):
    model = Movie
    class_serializer = MovieSerializer
    permission_post = IsAuthenticated   

class MovieOperations(APIView, MixinOperations):
    model = Movie
    class_serializer = MovieSerializer
    permission_post = IsAuthenticated
    permission_put = IsAuthenticated
    permission_delete = IsAuthenticated