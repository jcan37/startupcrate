from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'app.views.index', name='index'),
]
