from django.db import models
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from my_app.models import Task, SubTask, Category
from my_app.permissions import IsOwner
from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny
from my_app.serializers import RegisterSerializer, TaskSerializer, SubTaskSerializer, CategorySerializer


# Tasks


class TaskListCreateView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = ['status', 'deadline']

    search_fields = ['title', 'description']

    ordering_fields = ['created_at']
    ordering = ['created_at']


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    permission_classes = [IsAuthenticated, IsOwner]


    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


class SubTaskListCreateView(ListCreateAPIView):
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SubTask.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['created_at']


class SubTaskDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    def get_queryset(self):
        return SubTask.objects.filter(owner=self.request.user)


class TaskByDay(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        day = self._get_day_param(request)
        if day is not None:
            tasks = Task.objects.filter(owner=request.user, day=day)
        else:
            tasks = Task.objects.filter(owner=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_day_param(self, request):
        day_param = request.query_params.get('day')
        if not day_param:
            return None
        try:
            day = int(day_param)
            if 1 <= day <= 7:
                return day
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"day": "День должен быть от 1 до 7"})
        except ValueError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"day": "Должно быть целым числом"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_stats(request):
    user_tasks = Task.objects.filter(owner=request.user)

    total_count = user_tasks.count()
    status_data = user_tasks.values('status').annotate(total=Count('status'))
    by_status = {item['status']: item['total'] for item in status_data}
    overdue_count = user_tasks.filter(deadline__lt=timezone.now()).exclude(status='Done').count()

    return Response({
        "total_tasks": total_count,
        "status_breakdown": by_status,
        "overdue_tasks": overdue_count
    })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='count-tasks')
    def count_tasks(self, request):
        categories = self.get_queryset().annotate(
            tasks_count=Count('tasks', filter=models.Q(tasks__owner=request.user))
        )

        data = [
            {
                "id": category.id,
                "name": category.name,
                "tasks_count": category.tasks_count
            }
            for category in categories
        ]
        return Response(data)


AUTH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7
ACCESS_COOKIE_MAX_AGE = 60 * 15


def set_auth_cookies(response, refresh_token, access_token):
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=AUTH_COOKIE_MAX_AGE
    )
    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=ACCESS_COOKIE_MAX_AGE
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пользователь успешно зарегистрирован"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            response = Response({"message": "Вход выполнен успешно"}, status=status.HTTP_200_OK)
            set_auth_cookies(response, refresh, refresh.access_token)
            return response

        return Response({"error": "Неверный логин или пароль"}, status=status.HTTP_401_UNAUTHORIZED)


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token отсутствует"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            old_refresh = RefreshToken(refresh_token)
            new_refresh = RefreshToken.for_user(old_refresh.user)

            old_refresh.blacklist()

            response = Response({"message": "Токены успешно обновлены"}, status=status.HTTP_200_OK)
            set_auth_cookies(response, new_refresh, new_refresh.access_token)
            return response
        except (TokenError, User.DoesNotExist):
            return Response({"error": "Невалидный или просроченный токен"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        response = Response({"message": "Выход выполнен успешно"}, status=status.HTTP_200_OK)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')
        return response