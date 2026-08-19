from rest_framework import serializers
from .models import ActivityLogger

class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email',read_only=True)

    class Meta:
        model = ActivityLogger
        fields = ['id','user_email','action','metadata','created_at']
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.action == 'updated':
            changes = instance.metadata or {}
            fields_changed = list(changes.keys())
            data['message'] = f"{data['user_email']} updated {','.join(fields_changed)}"
        elif instance.action == 'created':
            data['message'] = f"{data['user_email'] } created this task"
        elif instance.action == 'deleted':
            data['message']=f"{data['user_email'] } deleted this task"
        return data