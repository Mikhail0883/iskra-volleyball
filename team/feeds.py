from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from .models import News


class LatestNewsFeed(Feed):
    title = "ВК «ИСКРА» - Последние новости"
    link = reverse_lazy('news_list')
    description = "Последние новости волейбольного клуба «ИСКРА»"

    def items(self):
        return News.objects.all()[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:200] + "..." if len(item.content) > 200 else item.content

    def item_pubdate(self, item):
        return item.created_at

    def item_link(self, item):
        return reverse_lazy('news_detail', kwargs={'slug': item.slug})
