from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .forms import *

def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    return render(request, "base.html", {"message" : "Login failed, your account is deactivated. Please contact the IT committee"})
            else:
                return render(request, "base.html", {
                    "message": "Login failed, incorrect password. Please <a href='" + reverse(
                        "login:login") + "'>try again</a>"})
    else:
        form = LoginForm()
    return render(request, 'login.html', {
        'form': form
    })

def logout(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    auth_logout(request)
    return render(request, "base.html", {"Message":"You are now logged out. <a href='/' title='Home'>Go back to the homepage</a>"})


def index(request):
    return render(request, 'index.html', {})
