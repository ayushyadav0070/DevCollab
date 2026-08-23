from django.db import models
from django.conf import settings
from  django.db.models  import Count


User = settings.AUTH_USER_MODEL

class Workspace(models.Model):
    name=models.CharField(max_length=255)
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name="owned_workspaces")
    created_at=models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        User,through='Membership',related_name='workspaces'
    )
   
    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=['owner', 'name'],
            name='unique_workspace_per_user'
            )   
        ]
    def __str__(self):
        return self.name
    
class Membership(models.Model):
    ROLE_CHOICES = (
        ('admin','Admin'),
        ('member','Member'),
        ('viewer','Viewer')
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='memberships')
    workspace = models.ForeignKey(Workspace,on_delete=models.CASCADE,related_name='memberships')

    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','workspace')
        indexes = [models.Index(fields=['user','workspace'])]
    def __str__(self):
        return f"{self.user}:{self.workspace} - {self.role}"