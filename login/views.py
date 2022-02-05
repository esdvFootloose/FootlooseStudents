from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .forms import *
from django.utils.http import is_safe_url
from django.conf import settings
from FootlooseStudents.secret import STUDENT_LOGIN_DISABLED

def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'], otp=form.cleaned_data['otp'])
            logger.debug(user)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    if 'next' in request.GET:
                        if is_safe_url(request.GET['next'], settings.SAFE_URL):
                            return HttpResponseRedirect(request.GET['next'])
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
        'form': form,
        'student_login_disabled' : STUDENT_LOGIN_DISABLED
    })

def logout(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    auth_logout(request)
    return render(request, "base.html", {"Message":"You are now logged out. <a href='/' title='Home'>Go back to the homepage</a>"})


def index(request):
    return render(request, 'index.html', {})
