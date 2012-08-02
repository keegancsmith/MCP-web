from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'mcpweb.views',
    url(r'^game/(\d+)/([a-zA-Z0-9]+/)?$', 'game', name='tron-game'),
)
