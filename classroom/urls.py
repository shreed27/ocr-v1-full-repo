from django.conf.urls.defaults import patterns, url
from classroom.views import ClassroomDelete

urlpatterns = patterns('intemass.classroom.views',
    url(r'^getall/$','getall',name='classroom_getall'),
    url(r'^add/$','add',name='classroom_add'),
    url(r'^updatename/$','classroom_updatename',name='classroom_updatename'),
    url(r'^delete/$',ClassroomDelete.as_view(),name='classroom_delete'),
	url(r'^getstudents/$','getstudents',name='classroom_getstudents'),
	)

