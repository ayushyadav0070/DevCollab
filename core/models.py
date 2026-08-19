from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL
# Create your models here.
class ActivityLogger(models.Model):
    ACTION_CHOICES = (
        ('created',"Created"),
        ('updated','Updated'),
        ('deleted','Deleted')
    )

    user = models.ForeignKey(
        User,on_delete=models.SET_NULL,
        null =True
    )
    action = models.CharField(max_length=20,choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')

    metadata = models.JSONField(default=dict,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['content_type','object_type']),
            models.INdex(fields = ['created_at'])
        ]
    def __str__(self):
        return f"{self.user} {self.action} {self.content_object}"