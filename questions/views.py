from django.http import Http404
from django.shortcuts import render

from .pagination import paginate

TAGS = ['алгебра', 'геометрия', 'уравнения', 'проценты', 'дроби']

QUESTIONS = []
for i in range(1, 101):
    QUESTIONS.append({
        'id': i,
        'title': 'Вопрос ' + str(i),
        'text': 'Текст вопроса ' + str(i),
        'tags': [TAGS[i % 5], TAGS[(i + 2) % 5]],
        'rating': i % 15,
        'answers_count': i % 7,
    })

ANSWERS = []
for i in range(1, 31):
    ANSWERS.append({
        'id': i,
        'text': 'Текст ответа ' + str(i),
        'rating': i % 6,
        'is_correct': i == 1,
    })


def index(request):
    page = paginate(QUESTIONS, request)
    return render(request, 'questions/index.html', {'page': page})


def hot(request):
    hot_questions = sorted(QUESTIONS, key=lambda q: q['rating'], reverse=True)
    page = paginate(hot_questions, request)
    return render(request, 'questions/hot.html', {'page': page})


def tag(request, tag_name):
    tag_questions = [q for q in QUESTIONS if tag_name in q['tags']]
    page = paginate(tag_questions, request)
    return render(request, 'questions/tag.html', {'page': page, 'tag_name': tag_name})


def question(request, question_id):
    if question_id < 1 or question_id > len(QUESTIONS):
        raise Http404('Вопрос не найден')
    item = QUESTIONS[question_id - 1]
    page = paginate(ANSWERS, request, per_page=5)
    return render(request, 'questions/question.html', {'question': item, 'page': page})


def ask(request):
    return render(request, 'questions/ask.html')
