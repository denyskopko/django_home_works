from rest_framework.decorators import api_view, action
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
#Tasks


class TaskListCreateView(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

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

    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class SubTaskPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'


class SubTaskListCreateView(ListCreateAPIView):

    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    pagination_class = SubTaskPagination
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
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer

class TaskByDay(APIView):
   def get(self, request):
       day = self._get_day_param(request)
       if day is not None:
           tasks = Task.objects.filter(day=day)
       else:
           tasks = Task.objects.all()
       serializer = TaskSerializer(tasks, many=True)
       return Response(serializer.data, status=status.HTTP_200_OK)
#
#
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
def task_stats(request):
    total_count = Task.objects.count()
    status_data = Task.objects.values('status').annotate(total=Count('status'))
    by_status = {item['status']: item['total'] for item in status_data}
    overdue_count = Task.objects.filter(deadline__lt=timezone.now()).exclude(status='Done').count()

    return Response({
        "total_tasks": total_count,
        "status_breakdown": by_status,
        "overdue_tasks": overdue_count
    })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=['get'], url_path='count-tasks')
    def count_tasks(self, request):
        categories = self.get_queryset().annotate(tasks_count=Count('tasks'))

        data = [
            {
                "id": category.id,
                "name": category.name,
                "tasks_count": category.tasks_count
            }
            for category in categories
        ]
        return Response(data)
