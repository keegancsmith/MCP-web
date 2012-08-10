from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns(
    'mcpweb.views',

    url(r'^game/(\d+)/$', 'game_viewer', name='tron-game'),
    url(r'^game/(\d+)/([a-zA-Z0-9]+)/$', 'game_api', name='tron-game-api'),

    url(r'^$', 'home', name='tron-home'),
    url(r'^new-game/$', 'new_game', name='new-tron-game'),
    url(r'^signup/$', 'signup', name='signup'),
    url(r'^login/$', 'login', name='login'),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
