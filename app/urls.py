from django.conf.urls import url
from .views import index, signup, signin, signout, crate, subscriptions, settings, change, cancel


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^signin/$', signin, name='signin'),
    url(r'^signout/$', signout, name='signout'),
    url(r'^crate/(?P<plan>1|3)/$', crate, name='crate'),
    url(r'^subscriptions/$', subscriptions, name='subscriptions'),
    url(r'^settings/$', settings, name='settings'),
    url(r'^change/(?P<subscription_id>\d+)/$', change, name='change'),
    url(r'^cancel/(?P<subscription_id>\d+)/$', cancel, name='cancel'),
]
