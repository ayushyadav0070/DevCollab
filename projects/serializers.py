from rest_framework import serializers
from .models import Projects  

class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Projects
        fields = ['id', 'name', 'workspace', 'created_by']
        read_only_fields = ['workspace','created_by']