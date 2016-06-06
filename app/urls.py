from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'app.views.index', name='index'),
    url(r'^signup/', 'app.views.signup', name='signup'),
    url(r'^signin/', 'app.views.signin', name='signin'),
    url(r'^crate/', 'app.views.crate', name='crate'),
    url(r'^subscriptions/', 'app.views.subscriptions', name='subscriptions'),
    url(r'^settings/', 'app.views.settings', name='settings'),
]
