from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnswerForm, CorrectForm, QuestionForm, VoteForm
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
    answers = Answer.objects.for_question(item)
    form = AnswerForm()
    per_page = 30
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), 'login')
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(request.user, item)
            ids = list(answers.values_list('pk', flat=True))
            number = ids.index(answer.pk) // per_page + 1
            return redirect(f'{item.get_absolute_url()}?page={number}#answer-{answer.pk}')
    page = paginate(answers, request, per_page=per_page)
    return render(request, 'questions/question.html', {
        'question': item, 'page': page, 'form': form,
    })


@login_required
def ask(request):
    form = QuestionForm()
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            return redirect(form.save(request.user))
    return render(request, 'questions/ask.html', {'form': form})


def vote(request, kind, item_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Используйте POST.'}, status=405, headers={'Allow': 'POST'})
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Войдите, чтобы поставить оценку.'}, status=401)
    model = {'question': Question, 'answer': Answer}.get(kind)
    item = model.objects.filter(pk=item_id).first() if model else None
    if item is None:
        return JsonResponse({'error': 'Вопрос или ответ не найден.'}, status=404)
    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Неверная оценка.'}, status=400)
    rating = form.save(request.user, item)
    if rating is None:
        return JsonResponse({'error': 'Вы уже поставили эту оценку.'}, status=409)
    return JsonResponse({'rating': rating})


def correct(request, question_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Используйте POST.'}, status=405, headers={'Allow': 'POST'})
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Войдите, чтобы отметить ответ.'}, status=401)
    item = Question.objects.filter(pk=question_id).first()
    if item is None:
        return JsonResponse({'error': 'Вопрос не найден.'}, status=404)
    if request.user.pk != item.author_id:
        return JsonResponse({'error': 'Отметить ответ может только автор вопроса.'}, status=403)
    form = CorrectForm(request.POST, item)
    if not form.is_valid():
        return JsonResponse({'error': 'Неверный ответ или отметка.'}, status=400)
    return JsonResponse({'checked': form.save()})
