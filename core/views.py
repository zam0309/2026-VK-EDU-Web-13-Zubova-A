from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.csrf import csrf_failure as csrf_error

from .forms import LoginForm, ProfileForm, SignupForm


login = LoginView.as_view(template_name='core/login.html', authentication_form=LoginForm)
logout = LogoutView.as_view(next_page='index')


def csrf_failure(request, reason=''):
    match = request.resolver_match
    if match and match.url_name in ('vote', 'correct'):
        return JsonResponse({'error': 'Обновите страницу и попробуйте снова.'}, status=403)
    return csrf_error(request, reason=reason)


def signup(request):
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            auth_login(request, form.save())
            return redirect('index')
    return render(request, 'core/signup.html', {'form': form})


@login_required
def profile(request):
    form = ProfileForm(instance=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    return render(request, 'core/profile.html', {'form': form})
