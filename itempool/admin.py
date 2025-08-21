from django.contrib import admin
from itempool.models import Itempool

class ItempoolAdmin(admin.ModelAdmin):
    filter_horizontal = ('accessible',)

admin.site.register(Itempool, ItempoolAdmin)
