from django.conf.urls.defaults import patterns, url
from itempool.views import ItempoolDelete
from django.contrib.auth.decorators import permission_required

urlpatterns = patterns('intemass.itempool.views',
    url(r'^add/$','itempool_add',name='itempool_add'),
    url(r'^getall/$','itempool_getall',name='itempool_getall'),
    url(r'^getquestions/$','itempool_getquestions',name='itempool_getquestions'),
    url(r'^updatename/$','itempool_updatename',name='itempool_updatename'),
    url(r'^updatedesc/$','itempool_updatedesc',name='itempool_updatedesc'),
    url(r'^teacherlist/$', 'getTeacherList', name='getTeacherList'),
    url(r'^addteacher/$', 'addteacher', name='addteacher'),
    url(r'^delete/$',permission_required('auth.add_user')(ItempoolDelete.as_view()),name='itempool_delete'),
)
