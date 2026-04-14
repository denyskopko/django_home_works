from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, viewsets
from rest_framework.views import APIView
from .models import Task, SubTask
from .serialisers import TaskSerializer, SubTaskSerializer
from django.db.models import Count
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination


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
# --- TASKS (Class Based Views) ---

class TaskByDay(APIView):
    def get(self, request):
        day = self._get_day_param(request)
        if day is not None:
            tasks = Task.objects.filter(day=day)
        else:
            tasks = Task.objects.all()
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


# --- SUBTASKS  ---
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


class SubTaskList(APIView, PageNumberPagination):
    page_size = 5

    def get(self, request: Request) -> Response:
        subtask_list = SubTask.objects.all().order_by('-created_at')
        task_title = request.query_params.get('task_title')
        status_param = request.query_params.get('status')
        if task_title:
            subtask_list = subtask_list.filter(task__title__icontains=task_title)
        if status_param:
            subtask_list = subtask_list.filter(status=status_param)
        results = self.paginate_queryset(subtask_list, request, view=self)
        serializer = SubTaskSerializer(results, many=True)

        return self.get_paginated_response(serializer.data)

    def get_page_size(self, request):
        # Оставляем вашу логику изменения размера страницы, если это разрешено
        page_size = request.query_params.get('page_size')
        if page_size and page_size.isdigit():
            return int(page_size)
        return self.page_size


class SubTaskDetailUpdateDeleteView(APIView, PageNumberPagination):
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

