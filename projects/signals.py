from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Projects

@receiver(post_save,sender=Projects)
@receiver(post_delete,sender=Projects)
def clear_project_cache(sender,instance,**kwargs):
    cache.delete_pattern(f"project_list_user_*_workspace_{instance.workspace_id}")
