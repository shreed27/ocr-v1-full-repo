from django.conf.urls.defaults import patterns, url
from report.views import feedback_popup, feedback_download

urlpatterns = patterns('intemass.report.views',
    url(r'^teacher/$', 'report_teacher', name='report_teacher'),
    url(r'^student/$', 'report_student', name='report_student'),
    url(r'^studentanswer/$', 'report_studentanswer', name='report_studentanswer'),
    url(r'^question/$', 'report_question', name='report_question'),
    url(r'^popup/(?P<pid>\d+)/(?P<stuid>\d+)/$', 'feedback_popup', name='feedback_popup'),
    url(r'^feedback_report/(?P<pid>\d+)/(?P<stuid>\d+)/$', 'feedback_popup', name='feedback_report'),
    url(r'^popup_pdf/(?P<pid>\d+)/(?P<stuid>\d+)/$', 'feedback_download', name='feedback_report_download'),
    #url(r'^classroom/$','report_classroom', name='report_classroom'),
    url(r'^get_closeness_report/$', 'get_closeness_report', name='get_closeness_report'),
    url(r'^csv_closeness_report/$', 'csv_closeness_report', name='csv_closeness_report'),
    url(r'^csv_closeness_report_summary/$', 'csv_closeness_report_summary', name='csv_closeness_report_summary'),
    )
