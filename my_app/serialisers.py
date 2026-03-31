from rest_framework import serializers
from .models import Task
"""Создайте эндпоинт для создания новой задачи. Задача должна быть создана с полями title, description, status, и deadline.
Шаги для выполнения:
Определите сериализатор для модели Task.
Создайте представление для создания задачи.
Создайте маршрут для обращения к представлению."""
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "deadline"]

