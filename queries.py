import os
from asyncio import all_tasks

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from my_app.models import Task, Category, SubTask
from django.utils import timezone
from datetime import timedelta

"""Создание записей:
Task:
title: "Prepare presentation".
description: "Prepare materials and slides for the presentation".
status: "New".
deadline: Today's date + 3 days.

SubTasks для SubTasks для "Prepare presentation":
    title: "Gather information".
    description: "Find necessary information for the presentation".
    status: "New".
    deadline: Today's date + 2 days.
title: "Create slides".
description: "Create presentation slides".
status: "New".
deadline: Today's date + 1 day."""


get_all = Task.objects.all()
print(get_all)

today = timezone.now()
three_days = timedelta(days=3)
one_day = timedelta(days=1)
two_days = timedelta(days=2)

prepare_task = Task.objects.create(title='Prepare presentation',
                                  description="Prepare materials and slides for the presentation",
                                  status='New',
                                  deadline=today+three_days)

prepare_subtask = SubTask.objects.create(title='Gather information',
                 description= "Find necessary information for the presentation",
                 status= "New",
                 deadline=today+two_days,
                 task=prepare_task)

slides_subtask = SubTask.objects.create(title="Create slides",
                                        description="Create presentation slides",
                                        status='New',
                                        deadline=today+one_day,
                                        task=prepare_task)

"""Чтение записей:
Tasks со статусом "New":
    Вывести все задачи, у которых статус "New".
SubTasks с просроченным статусом "Done":
    Вывести все подзадачи, у которых статус "Done", но срок выполнения истек."""

new_tasks= Task.objects.filter(status='New')
overdue_subtasks = SubTask.objects.filter(status='Done', deadline__lt = today)
print(new_tasks)

for subtask in overdue_subtasks:
    print(f"Подзадача: {subtask.title}, Дедлайн: {subtask.deadline}")

"""Изменение записей:
Измените статус "Prepare presentation" на "In progress".
Измените срок выполнения для "Gather information" на два дня назад.
Измените описание для "Create slides" на "Create and format presentation slides"."""

change_prepare = Task.objects.get(title="Prepare presentation")
change_prepare.status = "In progress"
change_prepare.deadline = today - two_days
change_prepare.save()

"""Удаление записей:
Удалите задачу "Prepare presentation" и все ее подзадачи."""

del_prepare = Task.objects.get(title='Prepare presentation')
del_prepare_subtasks = del_prepare.subtasks.all().delete()
del_prepare.delete()


all_tasks_new = Task.objects.all()
print()