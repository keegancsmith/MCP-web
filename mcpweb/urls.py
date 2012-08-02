from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'mcpweb.views',
    (r'.*', 'index'),
)
