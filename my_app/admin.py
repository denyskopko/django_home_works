from django.contrib import admin
from my_app.models import Task, SubTask, Category


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at', "deadline", "status")
    search_fields = ('title', 'created_at')
    ordering = ('-created_at',)

class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at', "deadline", "status")
    search_fields = ('title', 'created_at', "deadline")
    ordering = ('-created_at',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 5


admin.site.register(Task, TaskAdmin)
admin.site.register(SubTask, SubTaskAdmin)
admin.site.register(Category, CategoryAdmin)