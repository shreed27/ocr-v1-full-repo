from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('intemass.entity.views',
    url(r'^get/$','getentity',name='getentity'),
    url(r'^randomcode/add/$','generaterandomcode',name='generaterandomcode'),
                      )
