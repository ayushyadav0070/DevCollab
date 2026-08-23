from django.db import models
from django.conf import settings
from projects.models import Projects
# Create your models here.
User  =settings.AUTH_USER_MODEL



class TaskQuerySet(models.QuerySet):
    def for_user(self,user):
        return self.filter(
            project__workspace__members=user
        )
    def with_related (self):
        return self.select_related(
            'project',
            'assigned_to',
            'created_by'
        )
    def open(self):
        return self.filter(status ='to_do')
    def completed(self):
        return self.filter(status='done')
class Task(models.Model):
    
    objects = TaskQuerySet.as_manager()    
    STATUS_CHOICES = [
        ('to_do',"TO_DO"),
        ('in_progress','IN_PROGRESS'),
        ('done',"DONE"),
        ('abandoned','ABANDONED')
    ] 
    name = models.CharField(max_length=255,null=False,blank=False)
    status = models.CharField( max_length=20,choices=STATUS_CHOICES, default='to_do')
    project = models.ForeignKey(to=Projects,on_delete=models.CASCADE,related_name='tasks')
    assigned_to = models.ForeignKey(to=User,blank=True,null=True,on_delete=models.SET_NULL,related_name='assigned_tasks')
    created_by  =models.ForeignKey(to=User,on_delete=models.CASCADE,related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=255)
    title = models.CharField(max_length=255,blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['project','status']),
            models.Index(fields=['-created_at'])
        ]
    def __str__(self):
        return f"{self.title} project {self.project}"
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self._old_title =  self.title
    #     self._old_status = self.status

    # def save(self,*args,**kwargs):
    #     super().save(*args,**kwargs)
    #     self._old_status=self.status
    #     self._old_title = self.title
