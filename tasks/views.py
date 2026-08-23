from django.shortcuts import render
from rest_framework import settings
from .models import Task
from .serializers import TaskSerializer
from rest_framework import  status
from core.permissions import IsWorkforce
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import  IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from  workspaces.models import Membership
from core.models import ActivityLogger
from core.serializer import ActivityLogSerializer
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from core.pagination import TaskCursorPagination
from django.contrib.auth import get_user_model
from tasks.tasks import send_task_assignment_email
#user = get_user_model

class TaskViewset(ModelViewSet):
    pagination_class =TaskCursorPagination
    permission_classes=[IsWorkforce,IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.for_user(self.request.user).with_related()
    def perform_create(self, serializer):

        project_id = self.kwargs.get('project_pk')
        user = self.request.user

        membership = Membership.objects.filter(
            user=user, workspace__projects__id = project_id
        ).first()

        if not membership or membership.role == 'viewer':
            raise PermissionDenied('Viewers can\'t create tasks')

        task = serializer.save(
            project_id=project_id,
            created_by = self.request.user
        )
        if task.assigned_to:
            send_task_assignment_email.delay(
                task.assigned_to.email,
                task.title
            )
        
    @action(detail=True,methods=['post'])
    def change_status(self,request,pk = None):
        task=self.get_object()
        
        user = self.request.user

        membership = Membership.objects.filter(
            user=user,workspace = task.project.workspace
        ).first()

        if not membership or membership.role == 'viewer':
            raise PermissionDenied('Viewers can\'t change task status')
        
        new_status = request.data.get('status')
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response({'error': 'Invalid status'},status=400)
        task.status = new_status
        task.save()
        return Response({

            'status': 'Status updated'
        })
    @action(detail=True,methods=['get'],url_path='activity')
    def activity(self,request,pk=None):
        task = self.get_object()
        content_type = ContentType.objects.get_for_model(Task)

        logs = ActivityLogger.objects.filter(
            content_type=content_type,
            object_id = task.id
        ).order_by('-created_at').select_related('user')

        serializer = ActivityLogSerializer(logs,many =True)

        return Response(serializer.data)
