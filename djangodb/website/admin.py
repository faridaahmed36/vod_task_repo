from django.contrib import admin
from .models import Members, Tasks, Subscription

admin.site.register(Members)
admin.site.register(Tasks)
admin.site.register(Subscription)