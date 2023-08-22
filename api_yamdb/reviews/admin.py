from django.contrib import admin

from .models import Title, Category, Genre, ReviewComment, Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'text',
        'pub_date',
        'score'
    )
    list_editable = ('text',)
    search_fields = ('title', 'text',)


class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'text',
        'review',
        'pub_date'
    )
    list_editable = ('text',)
    search_fields = ('review', 'text',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "year",
        "description",
        "category",
    )
    search_fields = ('name', 'description')
    list_filter = ('year',)
    empty_value_display = 'empty'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(ReviewComment, ReviewCommentAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title, TitleAdmin)
