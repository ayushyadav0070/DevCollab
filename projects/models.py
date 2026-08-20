from django.db import models
from django.conf import settings
from workspaces.models import Workspace
from django.db.models import  Q,Count
User = settings.AUTH_USER_MODEL
class Projects(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    workspace =models.ForeignKey(
        to=Workspace,on_delete=models.CASCADE, related_name='projects'
    )    
    created_by = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='created_projects'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
  
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['workspace','name'],name='unique_project_per_workspace'
            )
        ]
    def __str__(self):
        return f"Project : {self.name} -> {self.workspace} "
    