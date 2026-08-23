from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from tasks.models import Task
from django.contrib.auth import get_user_model
@shared_task(bind=True,autoretry_for=(Exception,),retry_backoff=True, retry_kwargs={'max_retries':3})
def send_task_assignment_email(self,user_email,task_title):
    send_mail(
        subject="New Task Assigned",
        message = f"You have been assigned a new task titled {task_title}",
        from_email="//",
        recipient_list=[user_email],
    )

@shared_task
def mark_overdue_tasks():
    now =timezone.now()
    updated =Task.objects.filter(
        status='to_do',
        created_at__lt =now - timezone.timedelta(days=1)
    ).update(status='abandoned')
    return updated
@shared_task
def daily_digest():
    User = get_user_model()
    for user in User.objects.all():
        open_tasks = user.assigned_tasks.filter(status='to_do')
        if not open_tasks.exists():
            continue
        send_mail(
            subject="Daily Task Digest",
            message = f"You have {open_tasks.count()} open tasks",
            from_email="//",
            recipient_list=[user.email]
        )