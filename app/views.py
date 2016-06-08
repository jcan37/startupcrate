from app.models import Address, Subscription
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from itertools import chain
import stripe
stripe.api_key = "sk_test_7omNc4LQGjHI7viCIxfGfIr5"


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
    context = {'plan': plan, 'personal_addr': Address.objects.get(user=request.user, personal=True),
               'gift_addrs': Address.objects.filter(user=request.user, personal=False)}
    if request.method == 'POST':
        subscription = None
        stripe_plan = 'startupcrate_monthly' if plan == '1' else 'startupcrate_quarterly'
        if 'recipient' in request.POST:
            recipient = request.POST['recipient']
            address_id = request.POST['pastaddr']
            address = None
            if int(address_id) > 0:
                address = Address.objects.get(pk=address_id)
            if not address:
                address = Address(user=request.user, value=request.POST['newaddr'])
        else:
            recipient = '{0} {1}'.format(request.user.first_name, request.user.last_name)
            address = context['personal_addr']
        try:
            address.full_clean()
            address.save()
            subscription = Subscription(ship_address=address, recipient_name=recipient)
            subscription.full_clean()
            subscription.save()
            customer = stripe.Customer.create(source=request.POST['stripeToken'], plan=stripe_plan,
                                              email=request.POST['stripeEmail'])
            subscription.stripe_customer = customer['id']
            subscription.save()
            return HttpResponseRedirect('/subscriptions/')
        except Exception as e:
            print(e.message)
            context['invalid'] = True
            if subscription:
                subscription.delete()
    return render(request, 'app/crate.html', context)


@login_required
def subscriptions(request):
    if request.method == 'POST':
        print(request.POST)
        address_id = request.POST['pastaddr']
        address = None
        if int(address_id) > 0:
            address = Address.objects.get(pk=address_id)
        if not address:
            address = Address(user=request.user, value=request.POST['newaddr'])
        try:
            subscription = Subscription.objects.get(pk=request.POST['subscription_id'])
            address.full_clean()
            address.save()
            subscription.ship_address = address
            subscription.full_clean()
            subscription.save()
        except Exception as e:
            print(e.message)
    context = {
        'personal_subs': Subscription.objects.filter(
            ship_address=Address.objects.filter(user=request.user, personal=True)),
        'gift_addrs': Address.objects.filter(user=request.user, personal=False)
    }
    context['gift_subs'] = Subscription.objects.filter(ship_address__in=context['gift_addrs'])
    context['subscriptions'] = list(chain(context['personal_subs'], context['gift_subs']))
    return render(request, 'app/subscriptions.html', context)


@login_required
def settings(request):
    context = {'ship_addr': Address.objects.get(user=request.user, personal=True)}
    if request.method == 'POST':
        username = request.user.get_username()
        password = request.POST['password']
        if authenticate(username=username, password=password) is not None:
            if 'delete' in request.POST:
                user = request.user
                subs = Subscription.objects.filter(ship_address__in=Address.objects.filter(user=user))
                for subscription in subs:
                    subscription.stripe_cancel()
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


@login_required
def change(request, subscription_id):
    try:
        subscription = Subscription.objects.get(pk=subscription_id)
        subscription.stripe_change_plan()
    except Exception as e:
        print(e)
    return HttpResponseRedirect('/subscriptions/')


@login_required
def cancel(request, subscription_id):
    try:
        subscription = Subscription.objects.get(pk=subscription_id)
        subscription.stripe_cancel()
        subscription.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect('/subscriptions/')
