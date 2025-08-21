from django.conf.urls.defaults import patterns, url
from paper.views import PaperDelete
from django.contrib.auth.decorators import permission_required

urlpatterns = patterns('intemass.paper.views',
    url(r'^getall/$','paper_getall',name='paper_getall'),
    url(r'^getall_closeness/$','paper_getall_closeness',name='paper_getall_closeness'),
    url(r'^add/$','paper_add',name='paper_add'),
    url(r'^getquestions/$','paper_getquestions',name='paper_getquestions'),
    url(r'^delete/$',permission_required('auth.add_user')(PaperDelete.as_view()),name='paper_delete'),
    url(r'^info/$','getPaperInfoById',name='getPaperInfoById'),
    url(r'^updatename/$','paper_updatename',name='paper_updatename')

)

