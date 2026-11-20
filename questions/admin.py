from django.contrib import admin

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


class AnswerInline(admin.TabularInline):
    model = Answer
    fields = ['author', 'text', 'is_correct']
    readonly_fields = ['author']
    extra = 0
    show_change_link = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'created_at']
    search_fields = ['title', 'text', 'author__username']
    list_filter = ['created_at']
    list_select_related = ['author']
    autocomplete_fields = ['author', 'tags']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'author', 'is_correct', 'created_at']
    search_fields = ['text', 'question__title', 'author__username']
    list_filter = ['is_correct', 'created_at']
    list_select_related = ['question', 'author']
    autocomplete_fields = ['question', 'author']
    show_full_result_count = False


class TagFilter(admin.SimpleListFilter):
    title = 'Используется в вопросах'
    parameter_name = 'used'

    def lookups(self, request, model_admin):
        return [('yes', 'Да'), ('no', 'Нет')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(questions__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(questions__isnull=True)
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_filter = [TagFilter]


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'user', 'value']
    search_fields = ['question__title', 'user__username']
    list_filter = ['value']
    list_select_related = ['question', 'user']
    autocomplete_fields = ['question', 'user']
    show_full_result_count = False


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'answer', 'user', 'value']
    search_fields = ['answer__text', 'user__username']
    list_filter = ['value']
    list_select_related = ['answer', 'user']
    autocomplete_fields = ['answer', 'user']
    show_full_result_count = False
