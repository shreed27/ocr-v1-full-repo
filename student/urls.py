from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView
from portal.models import SProfile
from student.views import StudentDelete

urlpatterns = patterns('intemass.student.views',
    url(r'^index/$','student_index', name='student_index'),
    url(r'^getall/$','student_getall',name='student_getall'),
    url(r'^getbyname/$','student_getbyname',name='student_getbyname'),
    url(r'^add/$','student_add',name='student_add'),
    url(r'^modify/$','student_modify',name='student_modify'),
    url(r'^delete/$', StudentDelete.as_view(),name='student_delete'),
    url(r'^profile/(?P<pk>\d+)/$',
        DetailView.as_view(model=SProfile, template_name="student_profile.html"),
        name='student_profile'),
    url(r'^getassignedassignments/$','student_getassignedassignments',name='student_getassignedassignments'),
    url(r'^getcustompapers/$','student_getcustompapers',name='student_getcustompapers'),
    url(r'^takeassignment/$','student_takeassignment',name='student_takeassignment'),
    url(r'^custompaper/$','student_custompaper',name='student_custompaper'),
    url(r'^checktime/$','student_checktime',name='student_checktime'),
    url(r'^submitanswer/$','student_submitanswer',name='student_submitanswer'),
    url(r'^answersave/$','student_answersave',name='student_answersave'),
    url(r'^submitpaper/$','student_submitpaper',name='student_submitpaper'),
    url(r'^summarize/$','student_papersummarize',name='student_papersummarize'),
    url(r'^gethistoryanswers/$','student_getanswerrecords',
        name='student_getanswerrecords'),
    # OCR Integration URLs
    url(r'^ocr/upload/$','ocr_upload_answer_sheet', name='ocr_upload_answer_sheet'),
    url(r'^ocr/status/$','ocr_processing_status', name='ocr_processing_status'),
)
