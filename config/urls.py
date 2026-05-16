from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from my_app.views import (
    TaskListCreateView, TaskDetailView, SubTaskListCreateView, SubTaskDetailView,
    TaskByDay, task_stats, CategoryViewSet,
    RegisterView, LoginView, TokenRefreshView, LogoutView
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Task Manager API",
      default_version='v1',
      description="Документация для API управления задачами и подзадачами",
      terms_of_service="https://google.com",
      contact=openapi.Contact(email="contact@tasks.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

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

    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login/', LoginView.as_view(), name='auth_login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth_logout'),

    path(r'swagger<format>\.json|\.yaml', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

