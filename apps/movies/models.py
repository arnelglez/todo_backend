from django.db import models
import uuid

# Create your models here.

class Movie(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    title = models.CharField(max_length=100)
    overview = models.CharField(max_length=100)
    release_date = models.DateField()
    poster = models.ImageField(upload_to='posters/')
    backdrop = models.ImageField(upload_to='backdrops/')
    original_title = models.CharField(max_length=100)
    original_language = models.CharField(max_length=50)
    popularity = models.FloatField()
    vote_average = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title