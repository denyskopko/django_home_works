from django.utils import timezone
from rest_framework import serializers
from .models import Task, SubTask, Category


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "deadline"]


#----------------------------------------------------------------------------------------------------------------
class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = "__all__"



#----------------------------------------------------------------------------------------------------------------
class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = "__all__"


#----------------------------------------------------------------------------------------------------------------
class CreateSubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ["title", "description", "task", "status", "deadline"]
        read_only_fields = ["created_at"]


#----------------------------------------------------------------------------------------------------------------
class CategoryCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["name"]

    def create(self, validated_data):
        name = validated_data.get("name")
        if name is not None:
            category = Category.objects.get(name=name)
            if category:
                raise serializers.ValidationError("такая категория уже имеется")
            return super().create(validated_data)


    def update(self, instance, validated_data):
        name = validated_data.get("name")
        if name is not None:
            try :
                category = Category.objects.exclude(pk=instance.pk).get(name=name)
                if  category :
                    raise serializers.ValidationError("такая категория уже имеется")
            except Category.DoesNotExist:
                return super().update(instance, validated_data)
#----------------------------------------------------------------------------------------------------------------
"""Задание 4: Валидация данных в сериализаторах
Создайте TaskCreateSerializer и добавьте валидацию для поля deadline, чтобы дата не могла быть в прошлом. 
Если дата в прошлом, возвращайте ошибку валидации.
Шаги для выполнения:
Определите TaskCreateSerializer в файле serializers.py.
Переопределите метод validate_deadline для проверки даты."""
class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Дата deadline не может быть в прошлом")
        return value



    def create(self, validated_data):
         data_deadline= validated_data.get("deadline")
         if data_deadline < timezone.now():
            raise serializers.ValidationError("Дата deadline не может быть в прошлом")
         return super().create(validated_data)



