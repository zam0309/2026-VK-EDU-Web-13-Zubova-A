from django import forms
from django.db import transaction
from django.db.models import Sum

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


class QuestionForm(forms.ModelForm):
    title = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'title'}),
    )
    text = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'text', 'rows': 8}),
    )
    tags = forms.CharField(
        required=False, max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'tags'}),
    )

    class Meta:
        model = Question
        fields = ('title', 'text')

    def clean_tags(self):
        names = [name.strip() for name in self.cleaned_data['tags'].split(',') if name.strip()]
        names = list(dict.fromkeys(names))
        if len(names) > 3:
            raise forms.ValidationError('Можно добавить не больше трёх тегов.')
        for name in names:
            Tag._meta.get_field('name').clean(name, None)
        return names

    @transaction.atomic
    def save(self, user):
        question = super().save(commit=False)
        question.author = user
        question.save()
        for name in self.cleaned_data['tags']:
            tag, _ = Tag.objects.get_or_create(name=name)
            question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    text = forms.CharField(
        max_length=3000,
        widget=forms.Textarea(attrs={
            'class': 'form-control mb-1', 'rows': 4,
            'placeholder': 'Enter your answer here...', 'aria-label': 'Текст ответа',
        }),
    )

    class Meta:
        model = Answer
        fields = ('text',)

    def save(self, user, question):
        answer = super().save(commit=False)
        answer.author = user
        answer.question = question
        answer.save()
        return answer


class VoteForm(forms.Form):
    value = forms.TypedChoiceField(choices=[(1, '+'), (-1, '-')], coerce=int)

    @transaction.atomic
    def save(self, user, item):
        if isinstance(item, Question):
            model = QuestionLike
            target = {'question': item}
        else:
            model = AnswerLike
            target = {'answer': item}
        value = self.cleaned_data['value']
        vote, created = model.objects.get_or_create(user=user, defaults={'value': value}, **target)
        if not created:
            if vote.value == value:
                return None
            vote.value = value
            vote.save(update_fields=['value'])
        return model.objects.filter(**target).aggregate(rating=Sum('value'))['rating']


class CorrectForm(forms.Form):
    answer = forms.ModelChoiceField(queryset=Answer.objects.none())
    checked = forms.TypedChoiceField(choices=[('1', 'Да'), ('0', 'Нет')], coerce=int)

    def __init__(self, data, question):
        super().__init__(data)
        self.question = question
        self.fields['answer'].queryset = question.answers.all()

    @transaction.atomic
    def save(self):
        Question.objects.select_for_update().get(pk=self.question.pk)
        answer = self.cleaned_data['answer']
        if self.cleaned_data['checked']:
            self.question.answers.filter(is_correct=True).exclude(pk=answer.pk).update(is_correct=False)
            answer.is_correct = True
        else:
            answer.is_correct = False
        answer.save(update_fields=['is_correct'])
        return answer.is_correct
