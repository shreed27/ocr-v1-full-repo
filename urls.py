from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
                       url(r'^teacher/', include('intemass.teacher.urls')),
                       url(r'^student/', include('intemass.student.urls')),
                       url(r'^classroom/', include('intemass.classroom.urls')),
                       url(r'^itempool/', include('intemass.itempool.urls')),
                       url(r'^paper/', include('intemass.paper.urls')),
                       url(r'^question/', include('intemass.question.urls')),
                       url(r'^assignment/', include('intemass.assignment.urls')),
                       url(r'^common/', include('intemass.common.urls')),
                       url(r'^report/', include('intemass.report.urls')),
                       url(r'^entity/', include('intemass.entity.urls')),
                       url(r'^canvas/', include('intemass.canvas.urls')),
                       url(r'^mcq/', include('intemass.mcq.urls')),
                       url(r'^cpm/', include('intemass.cpm.urls')),
                       )

#portal
urlpatterns += patterns('intemass.portal.views',
                        url(r'^$', 'login', name='login'),
                        url(r'^api_login/$', 'api_login', name='api_login'),
                        url(r'^api_logout/$', 'api_logout', name='api_logout'),
                        url(r'^teacher-reg-api/$', 'teacher_registration_API', name='teacher_reg_api'),
                        url(r'^stud-reg-api/$', 'student_registration_API', name='student_reg_api'),
                        url(r'^home/$', 'index', name='index'),
                        url(r'^accounts/register/$', 'register', name='register'),
                        url(r'^accounts/login/$', 'login', name='login'),
                        url(r'^accounts/logout/$', 'logout', name='logout'),
                        url(r'^accounts/forgot-password/$', 'forgot_password', name='forgot_password'),
                        url(r'^accounts/info-modify/$', 'info_modify', name='info_modify'),
                        )


from django.conf import settings
urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }),
)