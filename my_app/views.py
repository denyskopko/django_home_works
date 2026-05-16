from django.db import models
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from .models import Task, SubTask, Category
from .serializers import TaskSerializer, SubTaskSerializer, CategorySerializer
from django.db.models import Count
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from permissions import IsOwner


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

