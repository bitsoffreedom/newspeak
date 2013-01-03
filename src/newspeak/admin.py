from django.contrib import admin

from .models import Feed, FeedEntry, KeywordFilter


class FeedAdmin(admin.ModelAdmin):
    filter_horizontal = ('filters', )
    search_fields = ('title', 'subtitle', 'description')
    list_display = ('title', 'url', 'active')
    list_filter = ('active', )


class FeedEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'published'
    list_display = ('published', 'title', 'feed')
    list_filter = ('feed', )
    search_fields = ('title', 'summary')


class KeywordFilterAdmin(admin.ModelAdmin):
    pass


admin.site.register(Feed, FeedAdmin)
admin.site.register(FeedEntry, FeedEntryAdmin)
admin.site.register(KeywordFilter, KeywordFilterAdmin)
