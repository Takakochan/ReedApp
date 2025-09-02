from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm
from django.contrib.auth import authenticate, login, logout
from usersettings.models import Checkbox_for_setting


def home_view(request):
    return render(request, 'home.html', {})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Checkbox_for_setting.objects.create(
                user=user,
                checkboxsetting=
                'temperature,humidity,cane_brand,harvest_year,gouging_machine,cane_diamater,thicness,hardness,flexibility,density,shaper,'
            )
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    error_message = None
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                else:
                    return redirect('home')

            else:
                error_message = 'Ups.Something went wrong...'

    return render(request, 'login.html', {
        'form': form,
        'error_message': error_message
    })
