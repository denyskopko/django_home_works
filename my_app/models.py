from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from datetime import datetime

STATUS_CHOICES = [
        ('New', 'New'),
        ('In progress', 'In progress'),
        ('Pending', 'Pending'),
        ('Blocked', 'Blocked'),
        ('Done', 'Done'),]

class Task(models.Model):
    title : str = models.CharField(max_length=100, unique_for_date="created_at", verbose_name="task title")
    description:str  = models.TextField(help_text='Описание задачи', verbose_name="task description")
    categories : str  = models.ManyToManyField("Category", related_name='tasks', blank=True, verbose_name='task categories')
    status :str  = models.CharField(max_length=15, choices=STATUS_CHOICES, default='New', verbose_name="task status")
    deadline : datetime = models.DateTimeField(help_text="Конечная дата выполнения", verbose_name="task deadline")
    created_at : datetime = models.DateTimeField(auto_now_add=True, verbose_name="task created at")

    class Meta:
        db_table = "task_manager_task"
        verbose_name = "Task"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_task_title')
        ]

    def __str__(self):
        return self.title
#----------------------------------------------------------------------------------------------------------

class Category(models.Model):
    name = models.CharField(max_length=55, unique=True)

    class Meta:
        db_table = "task_manager_category"
        verbose_name = "Category"
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_category_name')
        ]

    def __str__(self):
        return self.name
#--------------------------------------------------------------------------------------------------------------------

class SubTask(models.Model):
    title : str = models.CharField(verbose_name="Subtask title", max_length=100 )
    description:str = models.TextField(help_text='описание подзадачи',verbose_name="subtask description", validators=[MinLengthValidator(10), MaxLengthValidator(100)])
    task : Task = models.ForeignKey("Task", on_delete=models.PROTECT, related_name='subtasks', verbose_name="subtask task")
    status : str = models.CharField(max_length=15, choices=STATUS_CHOICES, default='New', verbose_name="subtask status")
    deadline : datetime = models.DateTimeField(help_text="", verbose_name="subtask deadline")
    created_at : datetime = models.DateTimeField(auto_now_add=True, verbose_name="subtask created at")

    class Meta:
        db_table = "task_manager_subtask"
        ordering = ['-created_at']
        verbose_name = "SubTask"
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_subtask_title')
        ]

    def __str__(self):
        return self.title