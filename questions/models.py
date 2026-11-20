from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Count, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse


class TagManager(models.Manager):
    def popular(self):
        return self.annotate(questions_count=Count('questions')).filter(
            questions_count__gt=0
        ).order_by('-questions_count', 'name')[:5]


class QuestionManager(models.Manager):
    def cards(self):
        likes = QuestionLike.objects.filter(question_id=OuterRef('pk'))
        rating = likes.values('question_id').annotate(total=Sum('value')).values('total')
        answers = Answer.objects.filter(question_id=OuterRef('pk'))
        count = answers.values('question_id').annotate(total=Count('pk')).values('total')
        return self.select_related('author__profile').prefetch_related('tags').annotate(
            rating=Coalesce(Subquery(rating), 0),
            answers_count=Coalesce(Subquery(count), 0),
        )

    def new(self):
        return self.cards().order_by('-created_at', '-pk')

    def hot(self):
        return self.cards().order_by('-rating', '-created_at', '-pk')

    def by_tag(self, tag):
        return self.hot().filter(tags=tag)


class AnswerManager(models.Manager):
    def for_question(self, question):
        return self.filter(question=question).select_related('author__profile').annotate(
            rating=Coalesce(Sum('likes__value'), 0)
        ).order_by('-rating', '-created_at', '-pk')


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=80, unique=True,
        validators=[
            RegexValidator(r'^[\w -]+\Z', 'Используйте буквы, цифры, пробелы, дефисы и подчёркивания.'),
        ],
    )

    objects = TagManager()

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', args=[self.name])


class Question(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name='Автор')
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='Теги', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        indexes = [models.Index(fields=['-created_at', '-id'])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question', args=[self.pk])


class Answer(models.Model):
    question = models.ForeignKey(
        Question, models.CASCADE, related_name='answers', verbose_name='Вопрос'
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name='Автор')
    text = models.TextField('Текст')
    is_correct = models.BooleanField('Правильный ответ', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    objects = AnswerManager()

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return self.text[:60]


VOTES = [(1, 'Плюс'), (-1, 'Минус')]


class QuestionLike(models.Model):
    question = models.ForeignKey(
        Question, models.CASCADE, related_name='likes', verbose_name='Вопрос'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name='Пользователь')
    value = models.SmallIntegerField('Оценка', choices=VOTES, default=1)

    class Meta:
        verbose_name = 'Оценка вопроса'
        verbose_name_plural = 'Оценки вопросов'
        unique_together = [('question', 'user')]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value__in=[-1, 1]), name='question_like_value'
            ),
        ]

    def __str__(self):
        return str(self.pk)


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, models.CASCADE, related_name='likes', verbose_name='Ответ')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, verbose_name='Пользователь')
    value = models.SmallIntegerField('Оценка', choices=VOTES, default=1)

    class Meta:
        verbose_name = 'Оценка ответа'
        verbose_name_plural = 'Оценки ответов'
        unique_together = [('answer', 'user')]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(value__in=[-1, 1]), name='answer_like_value'
            ),
        ]

    def __str__(self):
        return str(self.pk)
