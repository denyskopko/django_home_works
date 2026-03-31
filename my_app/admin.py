from django.contrib import admin
from my_app.models import Task, SubTask, Category


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ('title', 'status', 'deadline')


class TaskAdmin(admin.ModelAdmin):

    list_display = ('short_title', 'description', 'created_at', "deadline", "status")
    search_fields = ('title', 'created_at')
    ordering = ('-created_at',)
    inlines = [SubTaskInline]


    @admin.display(description="task title")
    def short_title(self, obj):
        if len(obj.title) > 10:
            return f"{obj.title[:10]}..."
        return obj.title


class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at', "deadline", "status")
    search_fields = ('title', 'created_at', "deadline")
    ordering = ('-created_at',)


    actions = ['set_status_done']

    @admin.action(description="Отметить как выполненные (Done)")
    def set_status_done(self, request, queryset):
        updated_count = queryset.update(status='Done')
        self.message_user(request, f"Статус 'Done' установлен для {updated_count} подзадач.")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 5


admin.site.register(Task, TaskAdmin)
admin.site.register(SubTask, SubTaskAdmin)
admin.site.register(Category, CategoryAdmin)
