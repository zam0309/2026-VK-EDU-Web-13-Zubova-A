from fractions import Fraction
from itertools import islice
from math import log2
from random import Random
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


TOPICS = [
    ('алгебра', 'Как упростить выражение 3x + {}x?'),
    ('геометрия', 'Как найти площадь квадрата со стороной {}?'),
    ('уравнения', 'Как решить уравнение 2x + {} = 81?'),
    ('проценты', 'Как найти {}% от числа 250?'),
    ('дроби', 'Как сократить дробь {}/120?'),
    ('арифметика', 'Как устно умножить {} на 11?'),
    ('статистика', 'Как найти среднее чисел 8, 12 и {}?'),
    ('вероятность', 'Как найти вероятность вытащить красный шар из {} шаров?'),
    ('функции', 'Как построить график функции y = {}x + 1?'),
    ('логарифмы', 'Как вычислить логарифм {} по основанию 2?'),
]
ANSWER_COUNTS = [0, 4, 7, 40, 5, 10, 12, 8, 6, 8]


def example(topic, x):
    examples = [
        ('Как сложить коэффициенты при x?',
         f'Сложи коэффициенты: 3 + {x} = {3 + x}. Ответ — {3 + x}x.',
         'Вынеси общий множитель x за скобки.'),
        ('Знаю длину стороны. Как по ней найти площадь?',
         f'Умножь сторону на себя: {x} × {x} = {x * x}. Это площадь квадрата.',
         'Все стороны квадрата равны, поэтому площадь равна квадрату стороны.'),
        ('Хочу оставить x в одной части уравнения. С чего начать?',
         f'Вычти {x} из обеих частей и раздели на 2. Получится x = {(81 - x) / 2:g}.',
         f'После вычитания {x} правая часть станет равна {81 - x}.'),
        ('Как перевести проценты в число для расчёта?',
         f'Раздели {x} на 100 и умножь на 250. Получится {x * 2.5:g}.',
         'Один процент от 250 равен 2,5. Умножь это число на количество процентов.'),
        ('Нужно записать дробь в несократимом виде.',
         f'Раздели числитель и знаменатель на их наибольший общий делитель. Получится {Fraction(x, 120)}.',
         'Чтобы сократить дробь, раздели числитель и знаменатель на одно и то же число.'),
        ('Ищу способ посчитать без калькулятора.',
         f'Умножь на 10 и прибавь исходное число: {x * 10} + {x} = {x * 11}.',
         'Представь 11 как сумму 10 и 1.'),
        ('Нужно найти среднее арифметическое трёх чисел.',
         f'Сложи числа и раздели сумму на 3: ({x} + 8 + 12) / 3 = {Fraction(x + 20, 3)}.',
         f'Сумма трёх чисел равна {x + 20}. Теперь раздели её на 3.'),
        ('Красный шар один. Каждый шар можно вытянуть с одинаковой вероятностью.',
         f'Благоприятный исход один, всего исходов {x}. Вероятность равна 1/{x}.',
         'Раздели число красных шаров на общее число шаров.'),
        ('Хочу построить прямую по двум точкам.',
         f'При x = 0 получаем y = 1, при x = 1 получаем y = {x + 1}. Проведи прямую через эти точки.',
         'Подставь x = 0, чтобы найти точку пересечения с осью y.'),
        ('Как найти показатель степени, если его сложно подобрать?',
         f'По формуле перехода к другому основанию получаем ln({x}) / ln(2) ≈ {log2(x):.3f}.',
         f'Логарифм показывает, в какую степень надо возвести 2, чтобы получить {x}.'),
    ]
    return examples[topic]


def chunks(items, size):
    items = iter(items)
    while True:
        batch = list(islice(items, size))
        if not batch:
            return
        yield batch


def save(model, items):
    for batch in chunks(items, 5000):
        model.objects.bulk_create(batch)


class Command(BaseCommand):
    help = 'Добавляет тестовые данные для AskPupkin'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio < 2:
            raise CommandError('ratio должен быть не меньше 2 для уникальных оценок.')

        fake = Faker('ru_RU')
        rng = Random()
        prefix = uuid4().hex[:12]
        users = [
            User(
                username=f'user_{prefix}_{i}',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=f'{prefix}_{i}@example.com',
                password='!',
                is_active=False,
            )
            for i in range(ratio)
        ]
        save(User, users)
        save(Profile, (Profile(user=user) for user in users))
        self.stdout.write('Пользователи и профили готовы.')

        names = [name for name, _ in TOPICS]
        topic_count = min(ratio, len(names))
        old_names = set(Tag.objects.filter(name__in=names).values_list('name', flat=True))
        last_id = Tag.objects.order_by('-pk').values_list('pk', flat=True).first() or 0
        tags = []
        for i in range(ratio):
            name = names[i % len(names)]
            if i >= len(names) or name in old_names:
                name = f'{name} задача {last_id + i + 1}'
            tags.append(Tag(name=name))
        save(Tag, tags)
        themes = dict(Tag.objects.filter(name__in=names).values_list('name', 'pk'))
        tags_by_topic = [tags[topic::topic_count] for topic in range(topic_count)]

        examples = {
            (topic, number): example(topic, number)
            for topic in range(len(TOPICS))
            for number in range(2, 99)
        }
        user_ids = [user.pk for user in users]
        links = Question.tags.through
        votes_per_question = min(5, ratio)
        extra_votes = (100 - 10 * votes_per_question) * ratio
        answer_start = 0

        for numbers in chunks(range(ratio * 10), 500):
            questions = [
                Question(
                    author_id=rng.choice(user_ids),
                    title=TOPICS[i % topic_count][1].format(i % 97 + 2),
                    text=examples[i % topic_count, i % 97 + 2][0],
                )
                for i in numbers
            ]
            save(Question, questions)
            question_tags = []
            for i, question in zip(numbers, questions):
                topic = i % topic_count
                choices = tags_by_topic[topic]
                tag = choices[(i // topic_count) % len(choices)]
                theme_id = themes.get(names[topic])
                question_tags.append(links(question_id=question.pk, tag_id=tag.pk))
                if theme_id and theme_id != tag.pk:
                    question_tags.append(links(question_id=question.pk, tag_id=theme_id))
            save(links, question_tags)
            save(QuestionLike, (
                QuestionLike(question_id=question.pk, user_id=user_id, value=rng.choice([1, 1, -1]))
                for question in questions
                for user_id in rng.sample(user_ids, votes_per_question)
            ))

            answers = [
                Answer(
                    question_id=question.pk,
                    author_id=rng.choice(user_ids),
                    text=examples[i % topic_count, i % 97 + 2][1 + j % 2],
                    is_correct=j == 0 and i % 3 == 0,
                )
                for i, question in zip(numbers, questions)
                for j in range(ANSWER_COUNTS[i % len(ANSWER_COUNTS)])
            ]
            save(Answer, answers)
            save(AnswerLike, (
                AnswerLike(answer_id=answer.pk, user_id=user_id, value=rng.choice([1, 1, -1]))
                for i, answer in enumerate(answers, start=answer_start)
                for user_id in rng.sample(user_ids, 1 + (i < extra_votes))
            ))
            answer_start += len(answers)

        self.stdout.write(self.style.SUCCESS(
            f'Добавлено: {ratio} пользователей, {ratio * 10} вопросов, '
            f'{ratio * 100} ответов, {ratio} тегов, {ratio * 200} оценок.'
        ))
