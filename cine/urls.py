from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'app.views.login_view'),
    url(r'^logout$', 'app.views.logout_view'),
    url(r'^films$', 'app.views.films'),
    url(r'^dispos$', 'app.views.dispos'),
    url(r'^votes$', 'app.views.votes'),
    url(r'^about$', 'app.views.about'),

    url(r'^admin/', include(admin.site.urls)),
)
