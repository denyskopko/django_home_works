from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from datetime import datetime

STATUS_CHOICES = [
        ('New', 'New'),
        ('In progress', 'In progress'),
        ('Pending', 'Pending'),
        ('Blocked', 'Blocked'),
        ('Done', 'Done'),
    ]

# Create your models here.
class Task(models.Model):
    """Модель Task:
    Описание: Задача для выполнения.
    Поля:
    title: Название задачи. Уникально для даты.
    description: Описание задачи.
    categories: Категории задачи. Многие ко многим.
    status: Статус задачи. Выбор из: New, In progress, Pending, Blocked, Done
    deadline: Дата и время дедлайн
    created_at: Дата и время создания. Автоматическое заполнение."""

    title : str = models.CharField(max_length=100, unique_for_date="created_at", verbose_name="task title")
    description:str  = models.TextField(help_text='Описание задачи', verbose_name="task description")
    categories : str  = models.ManyToManyField("Category", related_name='tasks', blank=True, verbose_name='task categories')
    status :str  = models.CharField(max_length=15, choices=STATUS_CHOICES, default='New', verbose_name="task status")
    deadline : datetime = models.DateTimeField(help_text="Конечная дата выполнения", verbose_name="task deadline")
    created_at : datetime = models.DateTimeField(auto_now_add=True, verbose_name="task created at")

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=55, unique=True)

    def __str__(self):
        return self.name

class SubTask(models.Model):
    """Описание: Отдельная часть основной задачи (Task).
    title: Название подзадачи.
    description: Описание подзадачи.
    task: Основная задача. Один ко многим.
    status: Статус задачи. Выбор из: New, In progress, Pending, Blocked, Done
    deadline: Дата и время дедлайн.
    created_at: Дата и время создания. Автоматическое заполнение."""
    title : str = models.CharField(verbose_name="Subtask title", max_length=100 )
    description:str = models.TextField(help_text='описание подзадачи',verbose_name="subtask description", validators=[MinLengthValidator(10), MaxLengthValidator(100)])
    task : Task = models.ForeignKey("Task", on_delete=models.PROTECT, related_name='subtasks', verbose_name="subtask task")
    status : str = models.CharField(max_length=15, choices=STATUS_CHOICES, default='New', verbose_name="subtask status")
    deadline : datetime = models.DateTimeField(help_text="", verbose_name="subtask deadline")
    created_at : datetime = models.DateTimeField(auto_now_add=True, verbose_name="subtask created at")

    def __str__(self):
        return self.title