from django.contrib import admin
from student.models import StudentAnswer

class StudentAnswerAdmin(admin.ModelAdmin):
	list_display = ('student', 'question', 'mark')

admin.site.register(StudentAnswer, StudentAnswerAdmin)
