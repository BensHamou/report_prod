from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(Line)
admin.site.register(Site)
admin.site.register(Team)
admin.site.register(Silo)
