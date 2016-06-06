from django.shortcuts import render


def index(request):
    return render(request, 'app/index.html')

def signup(request):
    return render(request, 'app/signup.html')

def signin(request):
    return render(request, 'app/signin.html')

def crate(request):
    return render(request, 'app/crate.html')

def subscriptions(request):
    return render(request, 'app/subscriptions.html')

def settings(request):
    return render(request, 'app/settings.html')
