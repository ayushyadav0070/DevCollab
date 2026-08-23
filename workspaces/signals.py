from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Workspace

@receiver(post_save,sender=Workspace)
@receiver(post_delete,sender=Workspace)
def clear_workspace_cache(sender,instance,**kwargs):
    for member in instance.members.all():
        cache.delete(f"workspace_list_user_{member.id}")