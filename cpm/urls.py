from django.conf.urls.defaults import patterns, url
from assignment.views import AssignmentDelete
from django.contrib.auth.decorators import permission_required
from cpm.views import CPM_ItempoolDelete , CPM_AssignmentDelete, OptionlistDelete, PaperDelete
urlpatterns = patterns('intemass.cpm.views',
	url(r'^main/$','index',name='cpm_index'),

	url(r'^itempool/add/$','itempool_add',name='cpm_itempool_add'),
	url(r'^itempool/del/$',permission_required('auth.add_user')(CPM_ItempoolDelete.as_view()),name='cpm_itempool_del'),
	url(r'^itempool/getquestions/$','get_cpm_question',name='get_cpm_question'),
	url(r'^itempool/updatename/$','cpm_itempool_updatename',name='cpm_itempool_updatename'),
	url(r'^itempool/updatedesc/$','cpm_itempool_updatedesc',name='cpm_itempool_updatedesc'),
	url(r'^itempool/teacherlist/$', 'getCPMTeacherList', name='getCPMTeacherList'),
	url(r'^itempool/addteacher/$', 'addCPMteacher', name='addCPMteacher'),


	url(r'^assignment/add/$','cpm_assignment_add',name='cpm_assignment_add'),
	url(r'^getall_paper/$','getall_cpm_paper',name='getall_cpm_paper'),
	url(r'^assignment/getstudents/$','cpm_assignment_getstudents',name='cpm_assignment_getstudents'),
	url(r'^getall_assignment/$','getall_cpm_assignment',name='getall_cpm_assignment'),
	url(r'^getall_itempool/$','getall_cpm_itempool',name='getall_cpm_itempool'),
	url(r'^assignment/updatename/$','cpm_assignment_updatename',name='cpm_assignment_updatename'),
	url(r'^assignment/del/$',permission_required('auth.add_user')(CPM_AssignmentDelete.as_view()),name='cpm_assignment_delete'), 


	url(r'^questioncategory/add/$','cpm_questioncategory_add',name='cpm_questioncategory_add'),
	url(r'^questioncategory/edit/$','cpm_questioncategory_edit',name='cpm_questioncategory_edit'),
	url(r'^questioncategory/view/$','cpm_questioncategory_view',name='cpm_questioncategory_view'),
	url(r'^questioncategory/save/$','cpm_questioncategory_save',name='cpm_questioncategory_save'),
	url(r'^questioncategory/addteacher/$', 'addCPMCategoryteacher', name='addCPMCategoryteacher'),
	url(r'^questioncategory/delete/$','cpm_questioncategory_delete',name='cpm_questioncategory_delete'),


	url(r'^paper/add/$','cpm_paper_add',name='cpm_paper_add'),
	url(r'^paper/del/$',permission_required('auth.add_user')(PaperDelete.as_view()),name='cpm_paper_delete'),
	url(r'^paper/getquestions/$','cpm_paper_getquestions',name='cpm_paper_getquestions'),
	url(r'^paper/updatename/$','cpm_paper_updatename',name='cpm_paper_updatename'),
	url(r'^paper/getall/$','cpm_paper_getall',name='cpm_paper_getall'),
	url(r'^paper/getall_closeness/$','cpm_paper_getall_closeness',name='cpm_paper_getall_closeness'),
	url(r'^paper/info/$','cpm_GetPaperInfoById',name='cpm_GetPaperInfoById'),


	url(r'^question/add/$','cpm_question_add',name='cpm_question_add'),
	url(r'^question/get/$','cpm_question_get',name='cpm_question_get'),
	url(r'^question/updatename/$','cpm_question_updatename',name='cpm_question_updatename'),
	url(r'^question/submit/$','cpm_question_submit',name='cpm_question_submit'),
	url(r'^question/stuget/$', 'cpm_stu_question_get', name='cpm_stu_question_get'),
	url(r'^question/getid/$','cpm_question_getid',name='cpm_question_getid'),
	url(r'^question/stureport/$', 'cpm_question_getstureport', name='cpm_question_getstureport'),


	url(r'^clozeanswer/getbyquestion/$','cpm_optionlist_getby_question',name='cpm_optionlist_getby_question'),


	url(r'^optionlist/teacherlist/$', 'getCPMCategoryTeacherList', name='getCPMCategoryTeacherList'),
	url(r'^clozelist/add/$','cpm_clozelist_add',name='cpm_clozelist_add'),
	url(r'^clozelist/updatename/$','cpm_clozelist_updatefield',name='cpm_clozelist_updatefield'),
	url(r'^clozelist/get/$','cpm_optionlist_get',name='cpm_optionlist_get'),
	url(r'^clozelist/del/$',permission_required('auth.add_user')(OptionlistDelete.as_view()),name='cpm_clozelist_del'),
	url(r'^student/fillinanswer/$','cpm_fillinanswer',name='cpm_fillinanswer'),




	url(r'^report/teacher/$','cpm_report_teacher',name='cpm_report_teacher'),
        url(r'^report/student/$','cpm_report_student',name='cpm_report_student'),
        url(r'^report/studentanswer/$','cpm_report_studentanswer',name='cpm_report_studentanswer'),
    	url(r'^report/popup/(?P<pid>\d+)/(?P<stuid>\d+)/$', 'cpm_feedback_popup', name='cpm_feedback_popup'),
    	url(r'^report/feedback_report/(?P<pid>\d+)/(?P<stuid>\d+)/$', 'cpm_feedback_popup', name='cpm_feedback_popup'),



	url(r'^student/index/$','cpm_student_index', name='cpm_student_index'),
	url(r'^student/getassignedassignments/$','cpm_student_getassignedassignments',name='cpm_student_getassignedassignments'),
        url(r'^student/takeassignment/$','cpm_student_takeassignment',name='cpm_student_takeassignment'),
       
)
