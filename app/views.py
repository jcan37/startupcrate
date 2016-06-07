from app.models import Address
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render


def index(request):
    return render(request, 'app/index.html')


def signup(request):
    if request.method == 'POST':
        context = {'fname': request.POST['fname'], 'lname': request.POST['lname'], 'email': request.POST['email'],
                   'ship_addr': request.POST['shipaddr'], 'gift_addr': request.POST['giftaddr']}
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.create_user(username, context['email'], password)
            user.first_name = context['fname']
            user.last_name = context['lname']
            user.full_clean()
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
        except Exception as e:
            print(e.message)
            context['user_exists'] = True
            return render(request, 'app/signup.html', context)
        shipping = Address(user=user, value=context['ship_addr'], personal=True)
        shipping.save()
        if len(context['gift_addr']) > 0:
            gift = Address(user=user, value=context['gift_addr'])
            gift.save()
        return HttpResponseRedirect('/')
    return render(request, 'app/signup.html')


def signin(request):
    errors = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                else:
                    return HttpResponseRedirect('/')
            else:
                errors['disabled'] = True
        else:
            errors['invalid'] = True
    return render(request, 'app/signin.html', errors)


def signout(request):
    logout(request)
    return HttpResponseRedirect('/signin/')


@login_required
def crate(request, plan):
    return render(request, 'app/crate.html', {'plan': plan})


@login_required
def subscriptions(request):
    return render(request, 'app/subscriptions.html')


@login_required
def settings(request):
    context = {'ship_addr': Address.objects.get(user=request.user, personal=True)}
    if request.method == 'POST':
        username = request.user.get_username()
        password = request.POST['password']
        if authenticate(username=username, password=password) is not None:
            if 'delete' in request.POST:
                user = request.user
                logout(request)
                user.delete()
                return HttpResponseRedirect('/signup/')
            request.user.first_name = request.POST['fname']
            request.user.last_name = request.POST['lname']
            request.user.email = request.POST['email']
            new_password = request.POST['newpass']
            if len(new_password) >= 8:
                request.user.set_password(new_password)
            try:
                request.user.full_clean()
                request.user.save()
                update_session_auth_hash(request, request.user)
                context['ship_addr'].value = request.POST['shipaddr']
                context['ship_addr'].full_clean()
                context['ship_addr'].save()
            except Exception as e:
                print(e.message)
                context['invalid_fields'] = True
            else:
                context['changes_saved'] = True
        else:
            context['invalid_credentials'] = True
    return render(request, 'app/settings.html', context)
