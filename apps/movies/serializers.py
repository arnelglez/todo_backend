from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.conf import settings
from urllib.parse import urlparse

from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    poster = Base64ImageField(required=False)
    backdrop = Base64ImageField(required=False)
    class Meta:
        model = Movie
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['poster']:
            representation["poster"] = self.get_base_url(instance.poster.url)
        if representation['backdrop']:
            representation["backdrop"] = self.get_base_url(instance.backdrop.url)
        return representation

    def validate(self, attrs):        
        if 'title' in attrs:
            if Movie.objects.filter(title=attrs['title']).exists():
                raise serializers.ValidationError('This movie already exists')
        return attrs

    def create(self, validated_data):
        return Movie.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.overview = validated_data.get('overview', instance.overview)
        instance.release_date = validated_data.get('release_date', instance.release_date)
        instance.poster = validated_data.get('poster', instance.poster)
        instance.backdrop = validated_data.get('backdrop', instance.backdrop)
        instance.original_title = validated_data.get('original_title', instance.original_title)
        instance.original_language = validated_data.get('original_language', instance.original_language)
        instance.popularity = validated_data.get('popularity', instance.popularity)
        instance.vote_average = validated_data.get('vote_average', instance.vote_average)
        instance.save()
        return instance

    def get_base_url(self, url):
        parsed_url = urlparse(url)
        production_url = f"{settings.DOMAIN}{parsed_url.path}"
        return production_url