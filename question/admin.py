from django.contrib import admin
from question.models import Question,StandardAnswer,QuestionImage, QuestionVideo

class QuestionAdmin(admin.ModelAdmin):
    filter_horizontal = ('accessible',)
admin.site.register(Question, QuestionAdmin)
admin.site.register(StandardAnswer)
admin.site.register(QuestionImage)
admin.site.register(QuestionVideo)
