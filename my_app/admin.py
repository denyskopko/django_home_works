from django.contrib import admin
from my_app.models import Task, SubTask, Category

# Register your models here.
admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(Category)
