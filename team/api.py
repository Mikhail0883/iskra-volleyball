from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Player, Match, News, Album, Season
from .serializers import *


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.AllowAny]


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [permissions.AllowAny]


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
def api_home(request):
    return Response({
        'message': 'Добро пожаловать в API ВК «ИСКРА»',
        'endpoints': {
            'players': '/api/players/',
            'matches': '/api/matches/',
            'news': '/api/news/',
            'albums': '/api/albums/',
            'current_season': '/api/current-season/',
        }
    })


@api_view(['GET'])
def current_season(request):
    season = Season.objects.filter(is_active=True).first()
    if season:
        serializer = SeasonSerializer(season)
        return Response(serializer.data)
    return Response({'error': 'Активный сезон не найден'})
