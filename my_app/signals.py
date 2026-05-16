from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from my_app.models import Task


@receiver(pre_save, sender=Task)
def check_task_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_task = Task.objects.get(pk=instance.pk)
            instance._status_changed = old_task.status != instance.status
            instance._old_status = old_task.status
        except Task.DoesNotExist:
            instance._status_changed = False
    else:
        instance._status_changed = True
        instance._old_status = None


@receiver(post_save, sender=Task)
def send_task_status_email(sender, instance, created, **kwargs):
    status_changed = getattr(instance, '_status_changed', False)

    if status_changed and instance.owner and instance.owner.email:
        if created:
            subject = f"Создана новая задача: {instance.title}"
            message_text = f"Здравствуйте, {instance.owner.username}!\n\nСоздана новая задача '{instance.title}' со статусом '{instance.status}'."
        else:
            subject = f"Изменение статуса задачи: {instance.title}"
            message_text = f"Здравствуйте, {instance.owner.username}!\n\nСтатус вашей задачи '{instance.title}' изменился с '{instance._old_status}' на '{instance.status}'."
        send_mail(
            subject=subject,
            message=message_text,
            from_email='webmaster@taskmanager.local',
            recipient_list=[instance.owner.email],
            fail_silently=False,
        )
