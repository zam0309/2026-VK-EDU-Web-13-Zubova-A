from django.shortcuts import get_object_or_404, render

from .models import Answer, Question, Tag
from .pagination import paginate


def question_list(request, questions, template, **context):
    context['page'] = paginate(questions, request)
    return render(request, template, context)


def index(request):
    return question_list(request, Question.objects.new(), 'questions/index.html')


def hot(request):
    return question_list(request, Question.objects.hot(), 'questions/hot.html')


def tag(request, tag_name):
    item = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(item)
    return question_list(request, questions, 'questions/tag.html', tag_name=item.name)


def question(request, question_id):
    item = get_object_or_404(Question.objects.cards(), pk=question_id)
    page = paginate(Answer.objects.for_question(item), request, per_page=30)
    return render(request, 'questions/question.html', {'question': item, 'page': page})


def ask(request):
    return render(request, 'questions/ask.html')
