from django.conf.urls.defaults import patterns, url
from assignment.views import AssignmentDelete
from django.contrib.auth.decorators import permission_required

urlpatterns = patterns('intemass.assignment.views',
    url(r'^getall/$','assignment_getall',name='assignment_getall'),
    url(r'^add/$','assignment_add',name='assignment_add'),
    url(r'^getstudents/$','assignment_getstudents',name='assignment_getstudents'),
    url(r'^delete/$',permission_required('auth.add_user')(AssignmentDelete.as_view()),name='assignment_delete'),
    url(r'^updatename/$','assignment_updatename',name='assignment_updatename'),
	)

