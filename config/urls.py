from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from my_app.views import (TaskListCreateView,TaskDetailView,SubTaskListCreateView,SubTaskDetailView,
                          TaskByDay,task_stats, CategoryViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('task/', TaskListCreateView.as_view()),
    path('task/<int:pk>/', TaskDetailView.as_view()),
    path('subtask/', SubTaskListCreateView.as_view()),
    path('subtask/<int:pk>/', SubTaskDetailView.as_view()),
    path('task/status/', task_stats),
    path('task/day/', TaskByDay.as_view()),

    path('', include(router.urls)),
]