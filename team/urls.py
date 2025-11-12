from django.urls import path, include
from . import views
from .feeds import LatestNewsFeed
from rest_framework.routers import DefaultRouter
from .api import *

router = DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'news', NewsViewSet)
router.register(r'albums', AlbumViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('players/', views.players, name='players'),
    path('matches/', views.matches, name='matches'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<int:album_id>/', views.album_detail, name='album_detail'),
    path('results/', views.our_results, name='our_results'),
    path('join/', views.join_team, name='join_team'),
    path('feeds/latest-news/', LatestNewsFeed(), name='news_feed'),
    path('table/', views.league_table, name='league_table'),

    # API routes
    path('api/', api_home, name='api_home'),
    path('api/current-season/', current_season, name='api_current_season'),
    path('api/', include(router.urls)),
]
