from rest_framework import serializers
from .models import Player, Match, News, Album, Photo, Season, Opponent


class OpponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opponent
        fields = ['id', 'name', 'logo']


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'name', 'is_active']


class PlayerSerializer(serializers.ModelSerializer):
    position_display = serializers.CharField(source='get_position_display', read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'name', 'number', 'position', 'position_display', 'photo', 'bio']


class MatchSerializer(serializers.ModelSerializer):
    opponent_name = serializers.CharField(source='opponent.name', read_only=True)
    season_name = serializers.CharField(source='season.name', read_only=True)
    result = serializers.CharField(read_only=True)
    is_win = serializers.BooleanField(read_only=True)
    points = serializers.IntegerField(read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'opponent', 'opponent_name', 'season', 'season_name',
            'date', 'location', 'is_home', 'sets_home', 'sets_away',
            'result', 'is_win', 'points'
        ]


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'slug', 'content', 'cover', 'created_at']


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'caption', 'uploaded_at']


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    photo_count = serializers.IntegerField(source='photos.count', read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'description', 'created_at', 'photos', 'photo_count']
