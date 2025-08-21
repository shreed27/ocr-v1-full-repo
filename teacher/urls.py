from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('intemass.teacher.views',
    url(r'^index/$', 'index', name='teacher_index'),
    url(r'^updatemark/$', 'updatemark', name='teacher_updatemark'),
    url(r'^updateomitted/$', 'updateomitted', name='teacher_updateomitted'),
)


