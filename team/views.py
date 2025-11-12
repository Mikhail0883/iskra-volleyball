from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.db import models
from .models import Player, Match, News, Album, Season, Opponent, NewsComment, LeagueStanding, PlayerApplication
from django.core.mail import send_mail
from django.conf import settings
from .forms import JoinForm, NewsCommentForm
from django.db.models import F

# Импорты для API (только если установлен rest_framework)
try:
    from rest_framework.decorators import api_view
    from rest_framework.response import Response

    REST_FRAMEWORK_AVAILABLE = True
except ImportError:
    REST_FRAMEWORK_AVAILABLE = False


def home(request):
    latest_news = News.objects.all()[:3]
    return render(request, 'team/home.html', {'latest_news': latest_news})


def players(request):
    # Безопасное кэширование с проверкой доступности
    try:
        cache_key = 'players_list'
        players_list = cache.get(cache_key)

        if not players_list:
            players_list = Player.objects.all()
            cache.set(cache_key, players_list, 60 * 60)  # 1 час
    except Exception:
        # Если кэширование не работает, используем обычный запрос
        players_list = Player.objects.all()

    return render(request, 'team/players.html', {'players': players_list})


def matches(request):
    matches_list = Match.objects.all()
    return render(request, 'team/matches.html', {'matches': matches_list})


def news_list(request):
    news_list = News.objects.all()
    paginator = Paginator(news_list, 5)  # 5 новостей на страницу

    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)

    return render(request, 'team/news_list.html', {'news': news})


def news_detail(request, slug):
    news_item = get_object_or_404(News, slug=slug)
    comments = news_item.comments.filter(is_approved=True)

    if request.method == 'POST':
        form = NewsCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news_item
            comment.save()
            return redirect('news_detail', slug=slug)
    else:
        form = NewsCommentForm()

    return render(request, 'team/news_detail.html', {
        'news': news_item,
        'comments': comments,
        'form': form
    })


def gallery(request):
    albums_list = Album.objects.all()
    paginator = Paginator(albums_list, 6)  # 6 альбомов на страницу

    page = request.GET.get('page')
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        albums = paginator.page(1)
    except EmptyPage:
        albums = paginator.page(paginator.num_pages)

    return render(request, 'team/gallery.html', {'albums': albums})


def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    photos_list = album.photos.all()

    paginator = Paginator(photos_list, 12)  # 12 фото на страницу
    page = request.GET.get('page')

    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        photos = paginator.page(1)
    except EmptyPage:
        photos = paginator.page(paginator.num_pages)

    return render(request, 'team/album_detail.html', {
        'album': album,
        'photos': photos
    })


def our_results(request):
    season = Season.objects.filter(is_active=True).first()
    if not season:
        return render(request, 'team/our_results.html', {
            'error': 'Активный сезон не задан в админке.'
        })

    # === Наши сыгранные матчи ===
    matches = Match.objects.filter(
        season=season
    ).annotate(
        total_sets=F('sets_home') + F('sets_away')
    ).filter(
        total_sets__gt=0  # Только сыгранные матчи
    ).select_related('opponent').order_by('-date')

    # Исправленный расчет статистики:
    stats = {
        'played': matches.count(),
        'wins': matches.filter(sets_home__gt=F('sets_away')).count(),
        'losses': matches.filter(sets_home__lt=F('sets_away')).count(),
        'sets_won': sum(m.sets_home for m in matches),
        'sets_lost': sum(m.sets_away for m in matches),
        'points': sum(m.points for m in matches),
    }

    # === Турнирная таблица ===
    standings = LeagueStanding.objects.filter(season=season).order_by('position')

    # Найдём позицию «ИСКРА»
    iskra_standing = None
    for item in standings:
        if 'ИСКРА' in item.team_name.upper():
            iskra_standing = item
            break

    return render(request, 'team/our_results.html', {
        'season': season,
        'stats': stats,
        'matches': matches,
        'standings': standings,
        'iskra_standing': iskra_standing,
    })


def calculate_standings(season):
    """Вспомогательная функция для расчета турнирной таблицы"""
    matches = Match.objects.filter(season=season)
    teams = {}

    teams['ИСКРА'] = {'played': 0, 'wins': 0, 'losses': 0, 'sets_won': 0, 'sets_lost': 0, 'points': 0}

    for opponent in Opponent.objects.all():
        teams[opponent.name] = {
            'played': 0, 'wins': 0, 'losses': 0,
            'sets_won': 0, 'sets_lost': 0, 'points': 0
        }

    for match in matches:
        opp_name = match.opponent.name

        teams['ИСКРА']['played'] += 1
        teams['ИСКРА']['sets_won'] += match.sets_home
        teams['ИСКРА']['sets_lost'] += match.sets_away
        teams['ИСКРА']['points'] += match.points

        teams[opp_name]['played'] += 1
        teams[opp_name]['sets_won'] += match.sets_away
        teams[opp_name]['sets_lost'] += match.sets_home
        teams[opp_name]['points'] += (3 - match.points)

        if match.is_win:
            teams['ИСКРА']['wins'] += 1
            teams[opp_name]['losses'] += 1
        else:
            teams['ИСКРА']['losses'] += 1
            teams[opp_name]['wins'] += 1

    return sorted(teams.items(), key=lambda x: x[1]['points'], reverse=True)


def join_team(request):
    if request.method == 'POST':
        form = JoinForm(request.POST)
        if form.is_valid():
            form.save()
            # Отправка email тренеру
            try:
                send_mail(
                    subject='Новая заявка в «ИСКРА»',
                    message=f"Имя: {form.cleaned_data['name']}\nТелефон: {form.cleaned_data['phone']}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['coach@iskra-volleyball.ru'],
                    fail_silently=True,
                )
            except Exception:
                # Продолжаем даже если email не отправился
                pass
            return render(request, 'team/join_success.html')
    else:
        form = JoinForm()
    return render(request, 'team/join.html', {'form': form})


# API функции (только если rest_framework доступен)
if REST_FRAMEWORK_AVAILABLE:
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
        from .serializers import SeasonSerializer
        season = Season.objects.filter(is_active=True).first()
        if season:
            serializer = SeasonSerializer(season)
            return Response(serializer.data)
        return Response({'error': 'Активный сезон не найден'})
else:
    # Заглушки если REST Framework не установлен
    def api_home(request):
        return render(request, 'team/api_unavailable.html')


    def current_season(request):
        return render(request, 'team/api_unavailable.html')


def league_table(request):
    season = Season.objects.filter(is_active=True).first()
    if not season:
        return render(request, 'team/league_table.html', {'error': 'Сезон не задан'})

    standings = LeagueStanding.objects.filter(season=season).order_by('position')

    # Найдём позицию «ИСКРА» (если есть)
    iskra = None
    for item in standings:
        if 'ИСКРА' in item.team_name.upper():
            iskra = item
            break

    return render(request, 'team/league_table.html', {
        'season': season,
        'standings': standings,
        'iskra': iskra,
    })
