from django.conf.urls.defaults import patterns, url
from question.views import QuestionDelete

urlpatterns = patterns('intemass.question.views',
                       url(r'^delete/$', QuestionDelete.as_view(), name='question_delete'),
                       url(r'^add/$', 'question_add', name='question_add'),
                       url(r'^imageupload/$', 'questionimage_upload', name='questionimage_upload'),
                       url(r'^updatename/$', 'question_updatename', name='question_updatename'),
                       url(r'^submit/$', 'question_submit', name='question_submit'),
                       url(r'^submitstandard/$', 'question_submitstandard', name='question_submitstandard'),
                       url(r'^alt_submitstandard/$', 'question_alt_submitstandard', name='question_alt_submitstandard'),
                       url(r'^submitmark/$', 'question_submitmark', name='question_submitmark'),
                       url(r'^alt_submitmark/$', 'question_alt_submitmark', name='question_alt_submitmark'),
                       url(r'^get/$', 'question_get', name='question_get'),
                       url(r'^stuget/$', 'stu_question_get', name='stu_question_get'),
                       url(r'^thumbnails/$', 'question_thumbnails', name='question_thumbnails'),
                       url(r'^studentthumbnails/$', 'stu_question_thumbnails', name='stu_question_thumbnails'),
                       url(r'^reportthumbnails/$', 'report_thumbnails', name='report_thumbnails'),
                       url(r'^deleteimage/$', 'question_deleteimage', name='question_deleteimage'),
                       url(r'^deletevideo/$', 'question_deletevideo', name='question_deletevideo'),
                       url(r'^pointmarklist/$', 'question_getpointmarklist', name='question_getpointmarklist'),
                       url(r'^stdanswer/$', 'question_getstdanswer', name='question_getstdanswer'),
                       url(r'^getid/$', 'questionid_get', name='questionid_get'),
                       url(r'^stureport/$', 'question_getstureport', name='question_getstureport'),
                       url(r'^saved/$', 'questionvideo_upload', name='saved')
                       )
