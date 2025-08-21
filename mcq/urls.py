from django.conf.urls.defaults import patterns, url
from assignment.views import AssignmentDelete
from django.contrib.auth.decorators import permission_required
from mcq.views import ItempoolDelete, OptionlistDelete,QuestionDelete,PaperDelete,MCQ_AssignmentDelete , MCQ_CanvasView,MCQ_OptionCanvasView
urlpatterns = patterns('intemass.mcq.views',
	url(r'^main/$','index',name='mcq_index'),
	url(r'^itempool/add/$','itempool_add',name='mcq_itempool_add'),
	url(r'^itempool/del/$',permission_required('auth.add_user')(ItempoolDelete.as_view()),name='mcq_itempool_del'),
	url(r'^getall_itempool/$','getall_mcq_itempool',name='getall_mcq_itempool'),
	url(r'^getall_paper/$','getall_mcq_paper',name='getall_mcq_paper'),
	url(r'^getall_assignment/$','getall_mcq_assignment',name='getall_mcq_assignment'),
	url(r'^itempool/getquestions/$','get_mcq_question',name='get_mcq_question'),
	url(r'^itempool/updatename/$','mcq_itempool_updatename',name='mcq_itempool_updatename'),
	url(r'^itempool/updatedesc/$','mcq_itempool_updatedesc',name='mcq_itempool_updatedesc'),
	url(r'^itempool/teacherlist/$', 'getMCQTeacherList', name='getMCQTeacherList'),
	url(r'^itempool/addteacher/$', 'addMCQteacher', name='addMCQteacher'),



	
	url(r'^questioncategory/view/$','mcq_questioncategory_view',name='mcq_questioncategory_view'),
	url(r'^questioncategory/empty/$','mcq_questioncategory_empty',name='mcq_questioncategory_empty'),
	url(r'^questioncategory/add/$','mcq_questioncategory_add',name='mcq_questioncategory_add'),
	url(r'^questioncategory/edit/$','mcq_questioncategory_edit',name='mcq_questioncategory_edit'),
	url(r'^questioncategory/save/$','mcq_questioncategory_save',name='mcq_questioncategory_save'),
	url(r'^questioncategory/delete/$','mcq_questioncategory_delete',name='mcq_questioncategory_delete'),
	url(r'^questioncategory/addteacher/$', 'addMCQCategoryteacher', name='addMCQCategoryteacher'),

	url(r'^question/add/$','mcq_question_add',name='mcq_question_add'),
	url(r'^question/updatename/$','mcq_question_updatename',name='mcq_question_updatename'),
	url(r'^question/get/$','mcq_question_get',name='mcq_question_get'),
	url(r'^question/getid/$','mcq_question_getid',name='mcq_question_getid'),
	url(r'^question/del/$',permission_required('auth.add_user')(QuestionDelete.as_view()),name='mcq_question_del'),
	url(r'^question/uploadimage/$','mcq_question_uploadimage',name='mcq_question_uploadimage'),
	url(r'^question/submit/$','mcq_question_submit',name='mcq_question_submit'),
	url(r'^question/thumbnails/$', 'mcq_question_thumbnails', name='mcq_question_thumbnails'),
	url(r'^question/deleteimage/$', 'mcq_question_deleteimage', name='mcq_question_deleteimage'),
	url(r'^question/stuget/$', 'mcq_stu_question_get', name='mcq_stu_question_get'),
	url(r'^question/stu_retake_get/$', 'mcq_stu_retake_question_get', name='mcq_stu_retake_question_get'),
	url(r'^question/stureport/$', 'mcq_question_getstureport', name='mcq_question_getstureport'),
	url(r'^question/reportthumbnails/$', 'mcq_report_thumbnails', name='mcq_report_thumbnails'),
	url(r'^question/studentthumbnails/$', 'mcq_stu_question_thumbnails', name='mcq_stu_question_thumbnails'),

	url(r'^optionlist/getbyquestion/$','mcq_optionlist_getby_question',name='mcq_optionlist_getby_question'),
	url(r'^optionlist/add/$','mcq_optionlist_add',name='mcq_optionlist_add'),
	url(r'^optionlist/updatename/$','mcq_optionlist_updatefield',name='mcq_optionlist_updatefield'),
	url(r'^optionlist/get/$','mcq_optionlist_get',name='mcq_optionlist_get'),
	url(r'^optionlist/del/$',permission_required('auth.add_user')(OptionlistDelete.as_view()),name='mcq_optionlist_del'),
	url(r'^optionlist/uploadimage/$', 'mcq_optionlist_uploadimage', name='mcq_optionlist_uploadimage'),
	url(r'^optionlist/thumbnails/$', 'mcq_optionlist_thumbnails', name='mcq_optionlist_thumbnails'),
	url(r'^optionlist/deleteimage/$', 'mcq_optionlist_deleteimage', name='mcq_optionlist_deleteimage'),
	url(r'^optionlist/teacherlist/$', 'getMCQCategoryTeacherList', name='getMCQCategoryTeacherList'),
	


	url(r'^paper/add/$','mcq_paper_add',name='mcq_paper_add'),
	url(r'^paper/del/$',permission_required('auth.add_user')(PaperDelete.as_view()),name='mcq_paper_delete'),
	url(r'^paper/getquestions/$','mcq_paper_getquestions',name='mcq_paper_getquestions'),
	url(r'^paper/updatename/$','mcq_paper_updatename',name='mcq_paper_updatename'),
	url(r'^paper/getall/$','mcq_paper_getall',name='mcq_paper_getall'),
	url(r'^paper/getall_closeness/$','mcq_paper_getall_closeness',name='mcq_paper_getall_closeness'),
	url(r'^paper/info/$','MCQ_GetPaperInfoById',name='MCQ_GetPaperInfoById'),



	url(r'^assignment/add/$','mcq_assignment_add',name='mcq_assignment_add'),
	url(r'^assignment/getstudents/$','mcq_assignment_getstudents',name='mcq_assignment_getstudents'),
	url(r'^assignment/updatename/$','mcq_assignment_updatename',name='mcq_assignment_updatename'),
	url(r'^assignment/del/$',permission_required('auth.add_user')(MCQ_AssignmentDelete.as_view()),name='mcq_assignment_delete'),


	url(r'^student/index/$','mcq_student_index', name='mcq_student_index'),
	url(r'^student/achod/$','mcq_student_achod', name='mcq_student_achod'),
	url(r'^student/getassignedassignments/$','mcq_student_getassignedassignments',name='mcq_student_getassignedassignments'),
	url(r'^student/getcustompapers/$','mcq_student_getcustompapers',name='mcq_student_getcustompapers'),
        url(r'^student/takeassignment/$','mcq_student_takeassignment',name='mcq_student_takeassignment'),
        url(r'^student/summarize/$','mcq_student_papersummarize',name='mcq_student_papersummarize'),
        url(r'^student/retakesummarize/$','mcq_student_retakepapersummarize',name='mcq_student_retakepapersummarize'),
        url(r'^student/selectedoption/$','mcq_student_selectedoption',name='mcq_student_selectedoption'),
        url(r'^student/selectedoption_retakepaper/$','mcq_student_selectedoption_retakepaper',name='mcq_student_selectedoption_retakepaper'),
        url(r'^student/custompaper/$','mcq_student_custompaper',name='mcq_student_custompaper'),
        url(r'^student/checktime/$','mcq_student_checktime',name='mcq_student_checktime'),
        url(r'^student/checktime_retake/$','mcq_student_retake_checktime',name='mcq_student_retake_checktime'),

	url(r'^student/getretakepapers/$','MCQ_student_getretakepapers',name='MCQ_student_getretakepapers'),
	url(r'^student/retakeassignment/$','mcq_student_re_takeassignment',name='mcq_student_re_takeassignment'),
        


        url(r'^report/teacher/$','mcq_report_teacher',name='mcq_report_teacher'),
        url(r'^report/student/$','mcq_report_student',name='mcq_report_student'),
        url(r'^report/studentanswer/$','mcq_report_studentanswer',name='mcq_report_studentanswer'),

    	url(r'^report/popup/(?P<pid>\d+)/(?P<stuid>\d+)/$', 'mcq_feedback_popup', name='mcq_feedback_popup'),
    	url(r'^report/feedback_report/(?P<pid>\d+)/(?P<stuid>\d+)/$', 'mcq_feedback_popup', name='mcq_feedback_popup'),

	url(r'^canvas/$', MCQ_CanvasView.as_view(), name='mcq_canvas'),
	url(r'^canvas/upload/$', 'mcq_canvas_upload', name='mcq_canvas_upload'),
	url(r'^canvas/get/$', 'mcq_canvas_get', name='mcq_canvas_get'),
	
	url(r'^optioncanvas/$', MCQ_OptionCanvasView.as_view(), name='mcq_optioncanvas'),
	url(r'^optioncanvas/upload/$', 'mcq_optioncanvas_upload', name='mcq_optioncanvas_upload'),
	url(r'^optioncanvas/get/$', 'mcq_optioncanvas_get', name='mcq_optioncanvas_get'),
	
	
	)



