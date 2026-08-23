from django.db.models.signals import post_delete,post_save,pre_save,pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Task
from core.models import ActivityLogger
from core.middleware import get_current_user
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(pre_save,sender=Task)
def track_old_values(sender,instance,**kwargs):
    if not instance.pk:
        return
    try:
        old =Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        return
    instance._old_status = old.status
    instance._old_title = old.title
@receiver(post_save,sender=Task)
def log_task(sender,instance,created,**kwargs):

    user = get_current_user() or instance.created_by
    content_type = ContentType.objects.get_for_model(Task)

    if created:
        ActivityLogger.objects.create(
            user=user,
            action = 'created',
            content_type=content_type,
            object_id = instance.id,
            metadata = {
                'title':instance.title,
                'status':instance.status
            }
        )
    else: #ondelete or other
        # try:
        #     old = Task.objects.get(pk=instance.pk)
        # except Task.DoesNotExist:
        #     return 
        changes = {}

        if hasattr(instance, '_old_status') and instance._old_status != instance.status:
            changes['status'] = {
                'from':instance._old_status , 'to':instance.status
            }
        if hasattr(instance, '_old_title') and instance._old_title != instance.title:
            changes['title'] = {
                'from':instance._old_title,
                'to': instance.title
            }
        if changes:
            ActivityLogger.objects.create(
                user=user,
            action = 'updated',
            content_type=content_type,
            object_id = instance.id,
            metadata = changes

            )

@receiver(pre_delete,sender=Task)
def log_task_delete(sender,instance,**kwargs):
    content_type = ContentType.objects.get_for_model(Task)
    
    ActivityLogger.objects.create(
        user = get_current_user() or  instance.created_by,
        action = 'deleted',
        content_type = content_type,
        object_id = instance.id
        , metadata={
            'title':instance.title
        }
    )

@receiver(post_save,sender=Task)
def broadcast_task_update(sender, instance,**kwargs):
    chl_lyrs = get_channel_layer()

    async_to_sync(chl_lyrs.group_send)(
        f"workspace_{instance.project.workspace_id}",
        {
            "type": "task_update",
            "data":{
                "id":instance.id,
                "status":instance.status,
                "title":instance.title
            }
        }
    )
