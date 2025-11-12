from django.db import models


class Player(models.Model):
    POSITION_CHOICES = [
        ('libero', 'Либеро'),
        ('setter', 'Связующий'),
        ('outside', 'Доигровщик'),
        ('opposite', 'Диагональный'),
        ('middle', 'Центральный'),
    ]

    name = models.CharField('Имя и фамилия', max_length=100)
    position = models.CharField('Позиция', max_length=20, choices=POSITION_CHOICES)
    number = models.PositiveSmallIntegerField('Номер')
    photo = models.ImageField('Фото', upload_to='players/', blank=True, null=True)
    bio = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __str__(self):
        return f"{self.name} (№{self.number})"


# ===== СЕЗОН =====
class Season(models.Model):
    name = models.CharField('Название сезона', max_length=100, help_text='Например: 2024/2025')
    is_active = models.BooleanField('Текущий сезон', default=True)

    class Meta:
        verbose_name = 'Сезон'
        verbose_name_plural = 'Сезоны'

    def __str__(self):
        return self.name


# ===== КОМАНДА-СОПЕРНИК (для таблицы) =====
class Opponent(models.Model):
    name = models.CharField('Название команды', max_length=100)
    logo = models.ImageField('Логотип', upload_to='opponents/', blank=True)

    class Meta:
        verbose_name = 'Соперник'
        verbose_name_plural = 'Соперники'

    def __str__(self):
        return self.name


# ===== ОБНОВЛЯЕМ Match — привязываем к сезону и сопернику =====
# Удали старую модель Match и замени на эту:
class Match(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name='Сезон')
    opponent = models.ForeignKey(Opponent, on_delete=models.CASCADE, verbose_name='Соперник')
    date = models.DateTimeField('Дата и время')
    location = models.CharField('Место проведения', max_length=200)
    is_home = models.BooleanField('Домашний матч', default=True)
    # Счёт по сетам: "3:1", "2:3" и т.д.
    sets_home = models.PositiveSmallIntegerField('Сеты (ИСКРА)', default=0)
    sets_away = models.PositiveSmallIntegerField('Сеты (Соперник)', default=0)

    # Дополнительно: можно добавить video_url, report_text и т.д.

    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
        ordering = ['date']

    def __str__(self):
        return f"{self.opponent} — {self.date.strftime('%d.%m.%Y')}"

    @property
    def result(self):
        return f"{self.sets_home}:{self.sets_away}"

    @property
    def is_win(self):
        return self.sets_home > self.sets_away

    @property
    def points(self):
        # 3 очка за победу 3:0 или 3:1, 2 за 3:2, 1 за 2:3, 0 за поражение
        if not (self.sets_home + self.sets_away):
            return 0
        if self.is_win:
            if self.sets_away <= 1:
                return 3
            else:
                return 2
        else:
            if self.sets_home == 2:
                return 1
            else:
                return 0


# ===== СТАТИСТИКА ИГРОКА ЗА МАТЧ =====
class PlayerMatchStat(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name='Игрок')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Матч')
    points = models.PositiveSmallIntegerField('Очки', default=0)
    aces = models.PositiveSmallIntegerField('Эйсы', default=0)  # подачи
    blocks = models.PositiveSmallIntegerField('Блоки', default=0)
    receptions = models.PositiveSmallIntegerField('Приёмы', default=0)

    class Meta:
        verbose_name = 'Статистика игрока за матч'
        verbose_name_plural = 'Статистика игроков'
        unique_together = ('player', 'match')

    def __str__(self):
        return f"{self.player} — {self.match}"


# ===== НОВОСТИ =====
class News(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL-метка', unique=True, blank=True)
    content = models.TextField('Текст новости')
    cover = models.ImageField('Обложка', upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)


# ===== АЛЬБОМЫ ДЛЯ ГАЛЕРЕИ =====
class Album(models.Model):
    title = models.CharField('Название альбома', max_length=150)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ===== ФОТО В АЛЬБОМЕ =====
class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, verbose_name='Альбом', related_name='photos')
    image = models.ImageField('Фото', upload_to='gallery/')
    caption = models.CharField('Подпись', max_length=200, blank=True)
    uploaded_at = models.DateTimeField('Загружено', auto_now_add=True)

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.album} — {self.caption or 'Фото'}"


class PlayerApplication(models.Model):
    POSITION_CHOICES = Player.POSITION_CHOICES  # берём из Player

    name = models.CharField('Имя', max_length=100)
    age = models.PositiveSmallIntegerField('Возраст')
    position = models.CharField('Позиция', max_length=20, choices=POSITION_CHOICES)
    experience = models.TextField('Опыт', blank=True)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на вступление'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f"{self.name} ({self.position})"


# ===== КОММЕНТАРИИ К НОВОСТЯМ =====
class NewsComment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name='Новость', related_name='comments')
    author_name = models.CharField('Имя автора', max_length=100)
    email = models.EmailField('Email', blank=True)
    content = models.TextField('Текст комментария', max_length=1000)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_approved = models.BooleanField('Одобрен', default=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.author_name} к {self.news.title}"


class LeagueStanding(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name='Сезон')
    team_name = models.CharField('Название команды', max_length=100)
    position = models.PositiveSmallIntegerField('Место')
    played = models.PositiveSmallIntegerField('И', default=0, help_text='Игры')
    wins = models.PositiveSmallIntegerField('В', default=0)
    losses = models.PositiveSmallIntegerField('П', default=0)
    sets_won = models.PositiveSmallIntegerField('Сеты+', default=0)
    sets_lost = models.PositiveSmallIntegerField('Сеты-', default=0)
    points = models.PositiveSmallIntegerField('Очки', default=0)

    class Meta:
        verbose_name = 'Позиция в таблице'
        verbose_name_plural = 'Турнирная таблица'
        ordering = ['season', 'position']

    def __str__(self):
        return f"{self.position}. {self.team_name} — {self.points} очков"
