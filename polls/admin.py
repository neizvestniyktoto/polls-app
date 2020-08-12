from django.contrib import admin

from .models import Choice, Question, Author, Comment


class AuthorAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'first_name', 'last_name', 'birth_date']}),
    ]
    list_display = ['first_name', 'last_name', 'birth_date']
    search_fields = ['first_name',  'last_name']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class CommentInLine(admin.TabularInline):
    model = Comment


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
        (None, {'fields': ['author']}),
    ]
    inlines = [ChoiceInline, CommentInLine]
    list_display = ('question_text', 'pub_date', 'author', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text', 'author']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Author, AuthorAdmin)
