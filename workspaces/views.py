from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Workspace , Membership
from .serializer import WorkspaceSerializer ,AddMemberSerializer , WorkspaceMemberSerializer
from core.permissions import IsWorkforce,IsWorkforceAdmin
from django.conf import settings
from django.contrib.auth import get_user_model
from  tasks.models import Task
from core.serializer import ActivityLogSerializer
from core.models import ActivityLogger
from django.contrib.contenttypes.models import ContentType
from core.pagination import WorkspacePagePagination
from django.db.models import Count
from django.db import connection
from django.core.cache import cache
User = get_user_model()

class WorkspaceViewSet(ModelViewSet):
    pagination_class = WorkspacePagePagination
    permission_classes = [IsAuthenticated,IsWorkforce]
    serializer_class =WorkspaceSerializer
    
    def list(self, request, *args, **kwargs):
        user = request.user
        cache_key = f'workspace_list_user_{user.id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        queryset=self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        response = self.get_paginated_response(serializer.data)
        cache.set(cache_key,response.data,timeout=60)

        return Response(response) 

    def get_queryset(self):
        return Workspace.objects.filter(
            members=self.request.user
        ).select_related('owner'
        ).annotate(
            project_count = Count('projects',distinct=True),
            member_count =Count('memberships',distinct=True)
        )
    
    @action(detail=True,methods=['post'],url_path='add-member')
    def add_member(self,request,pk=None):
        workspace = self.get_object()

        membership = Membership.objects.filter(
            user = request.user
            , workspace=workspace
        ).first()

        if not membership or membership.role != 'admin':
            return Response(
                {
                    'error':'Only admins can add memebers'
                },status=status.HTTP_403_FORBIDDEN
            ) 
        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_user = serializer.validated_data['user']
        validated_role =serializer.validated_data['role']
        if Membership.objects.filter(user =validated_user, workspace=workspace).exists():
            return Response(
                {
                    'error':'user already a memeber'
                },status=status.HTTP_400_BAD_REQUEST
            )
        Membership.objects.create(
            user=validated_user,
            workspace=workspace,
            role=validated_role
        )
        return Response({
            'message':f'User added succesfully '
        })
    @action(detail=True, methods=['delete'], url_path='rem-member',
            permission_classes=[IsAuthenticated, IsWorkforceAdmin])
    def remove_member(self, request, pk=None):
        workspace = self.get_object()

        github_id = request.data.get('github_id')

        if not github_id:
            return Response({'error': 'github_id is required'}, status=400)

        user_to_remove = User.objects.filter(github_id=github_id).first()

        if not user_to_remove:
            return Response({'error': 'User not found'}, status=400)

        membership = Membership.objects.filter(
            user=user_to_remove,
            workspace=workspace
        ).first()

        if not membership:
            return Response({'error': 'User not in this workspace'}, status=400)

        membership.delete()

        return Response({
            'message': f'{user_to_remove} removed from workspace {workspace.name}'
        })
    @action(detail=True, methods=['get'], url_path='members',
            permission_classes=[IsAuthenticated,IsWorkforce])
    def list_members(self,request,pk =None):
        workspace = self.get_object()

        membership = workspace.memberships.select_related('user').all()

        serializer = WorkspaceMemberSerializer(membership,many = True)

        return Response(serializer.data)
    @action(detail=True,methods =['get'],url_path='activity')
    def workspace_activity(self,request,pk=None):
        workspace = self.get_object()
        tasks = Task.objects.filter(project__workspace=workspace).values_list('id', flat=True)
        content_type  =ContentType.objects.get_for_model(Task)

        logs = ActivityLogger.objects.filter(
            content_type=content_type,
            object_id__in=tasks
        ).select_related('user').order_by('-created_at')
        serializer  = ActivityLogSerializer(logs,many=True)

        return Response(serializer.data)
    
    @action(detail=True,methods=['get'],url_path='report')
    def report(self,request,pk=None):
        with connection.cursor() as cursor:
            cursor.execute(

                """
                SELECT p.id, p.name, COUNT(t.id) AS task_count
            FROM projects_project p
            LEFT JOIN tasks_task t ON t.project_id = p.id
            WHERE p.workspace_id = %s
            GROUP BY p.id;
            """
            ,[pk])
            columns = [col[0] for col in cursor.description]
            results=[
                dict(zip(columns,row))
                for row in cursor.fetchall()
            ]
        return Response(results)