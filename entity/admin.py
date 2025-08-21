from django.contrib import admin
from entity.models import Years, Levels, Subjects, Randomcode

class RandomcodeAdmin(admin.ModelAdmin):
    list_display = ('randomcode','used',)
    list_filter = ('used',)

admin.site.register(Years)
admin.site.register(Levels)
admin.site.register(Subjects)
admin.site.register(Randomcode, RandomcodeAdmin)
