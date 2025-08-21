from django.contrib import admin
from portal.models import TProfile,SProfile

class TPadmin(admin.ModelAdmin):
	list_display = ('user', 'gender', 'cellphone')
	list_filter = ('user', 'gender', 'cellphone')

admin.site.register(TProfile, TPadmin)

class SPadmin(admin.ModelAdmin):
	list_display = ('user', 'gender', 'cellphone','classroom')
	list_filter = ('user', 'gender', 'cellphone','classroom')

admin.site.register(SProfile,SPadmin)
