from django.contrib import admin
from .models import Player, Match, News, Album, Photo, Season, Opponent, PlayerMatchStat, NewsComment, LeagueStanding


# === Игроки и матчи (оставляем) ===
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'position')
    list_filter = ('position',)
    search_fields = ('name',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('opponent', 'date', 'location', 'result', 'points')
    list_filter = ('season', 'is_home')
    ordering = ('date',)


# === НОВОСТИ ===
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at',)


# === АЛЬБОМЫ и ФОТО ===
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 5  # сколько пустых форм показывать


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    inlines = [PhotoInline]
    list_display = ('title', 'created_at', 'photo_count')
    readonly_fields = ('created_at',)

    def photo_count(self, obj):
        return obj.photos.count()

    photo_count.short_description = 'Фото'


# === СЕЗОНЫ ===
@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')


# === СОПЕРНИКИ ===
@admin.register(Opponent)
class OpponentAdmin(admin.ModelAdmin):
    list_display = ('name',)


# === СТАТИСТИКА ===
@admin.register(PlayerMatchStat)
class PlayerMatchStatAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'points', 'aces', 'blocks')
    list_filter = ('match__season', 'player')


@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'news', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('author_name', 'content')


@admin.register(LeagueStanding)
class LeagueStandingAdmin(admin.ModelAdmin):
    list_display = ('position', 'team_name', 'played', 'wins', 'losses', 'sets_won', 'sets_lost', 'points', 'season')
    list_filter = ('season',)
    ordering = ('season', 'position')
