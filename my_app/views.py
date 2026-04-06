from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.views import APIView
from .models import Task, SubTask
from .serialisers import TaskSerializer, SubTaskSerializer
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

"""Задание 5: Создание классов представлений
Создайте классы представлений для работы с подзадачами (SubTasks), включая создание, получение, обновление
 и удаление подзадач. Используйте классы представлений (APIView) для реализации этого функционала.
Шаги для выполнения:
Создайте классы представлений для создания и получения списка подзадач (SubTaskListCreateView).
Создайте классы представлений для получения, обновления и удаления подзадач (SubTaskDetailUpdateDeleteView).
Добавьте маршруты в файле urls.py, чтобы использовать эти классы."""


class SubTaskListCreateView(APIView):
    def get (self, request:Request)->Response:
        subtask_list = SubTask.objects.all()
        serializer = SubTaskSerializer(subtask_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


    def post(self, request:Request)->Response:
        try:
            serializer = SubTaskSerializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    def get(self, request:Request, pk)->Response:
        try:
            obj = SubTask.objects.get(pk=pk)
            serializer = SubTaskSerializer(obj)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except SubTask.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": str(e)})

    def put(self, request:Request, pk)->Response:
        try:
            obj = SubTask.objects.get(pk=pk)
            serializer = SubTaskSerializer(obj, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except SubTask.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": str(e)})


    def delete(self, request:Request, pk)->Response:
        try:
            obj = SubTask.objects.get(pk=pk)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SubTask.DoesNotExist as e:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": str(e)})











