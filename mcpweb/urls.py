from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    'mcpweb.views',
    url(r'^game/(\d+)/([a-zA-Z0-9]+/)?$', 'game', name='tron-game'),

    url(r'^admin/', include(admin.site.urls)),
)
