from rest_framework import serializers
from .models import Workspace,Membership
from django.contrib.auth import get_user_model

User = get_user_model()
class WorkspaceSerializer(serializers.ModelSerializer):

    project_count = serializers.IntegerField(read_only=True)
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Workspace
        fields = ['id','name','project_count','member_count']
    def validate(self,data):
        user  = self.context['request'].user
        name = data.get('name')

        if Workspace.objects.filter(owner=user,name=name).exists():
            raise serializers.ValidationError(
                'You already a workspace with this name'
            )
        return data
    def create(self,validated_data):
        user = self.context['request'].user
        workspace =  Workspace.objects.create(
            name=validated_data['name'],
            owner=user
        )

        Membership.objects.create(
            user=user,
            workspace=workspace,
            role='admin'
        )

        return workspace 

class AddMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=['admin','member','viewer'])

    def validate(self, data):
        email = data['email']

        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user exists')
        data['user']=user

        return data
    
class WorkspaceMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Membership
        fields = ['email', 'role', 'joined_at']