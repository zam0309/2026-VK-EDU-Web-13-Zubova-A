import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, validators=[django.core.validators.RegexValidator('^[\\w -]+\\Z', 'Используйте буквы, цифры, пробелы, дефисы и подчёркивания.')], verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('text', models.TextField(verbose_name='Текст')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('tags', models.ManyToManyField(blank=True, related_name='questions', to='questions.tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Правильный ответ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='questions.question', verbose_name='Вопрос')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.CreateModel(
            name='AnswerLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 'Плюс'), (-1, 'Минус')], default=1, verbose_name='Оценка')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='questions.answer', verbose_name='Ответ')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка ответа',
                'verbose_name_plural': 'Оценки ответов',
                'constraints': [models.CheckConstraint(condition=models.Q(('value__in', [-1, 1])), name='answer_like_value')],
                'unique_together': {('answer', 'user')},
            },
        ),
        migrations.CreateModel(
            name='QuestionLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(1, 'Плюс'), (-1, 'Минус')], default=1, verbose_name='Оценка')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='questions.question', verbose_name='Вопрос')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка вопроса',
                'verbose_name_plural': 'Оценки вопросов',
                'constraints': [models.CheckConstraint(condition=models.Q(('value__in', [-1, 1])), name='question_like_value')],
                'unique_together': {('question', 'user')},
            },
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['-created_at', '-id'], name='questions_q_created_79cadc_idx'),
        ),
    ]
