from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serialisers import TaskSerializer
from django.db.models import Count
from django.utils import timezone

"""Создайте эндпоинт для создания новой задачи. Задача должна быть создана с полями title, description, status, и deadline.
Шаги для выполнения:
Определите сериализатор для модели Task.
Создайте представление для создания задачи.
Создайте маршрут для обращения к представлению."""


@api_view(['POST'])
def create_task(request):
        try:
            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as err:
            return Response(data={"error": f"Validation error: {err}"},status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_tasks_by_id(request, pk):
    try:
        task = Task.objects.get(id=pk)
    except Task.DoesNotExist as e:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"error": str(e)})
    serializer = TaskSerializer(task)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


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