from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsWorkforce
from rest_framework import status
from django.conf import settings
from rest_framework.response import Response
from .models import Projects
from .serializers import ProjectSerializer
from  workspaces.models import Membership
from django.db.models import Count,Q
from rest_framework.exceptions import PermissionDenied
from django.core.cache import cache
class ProjectViewset(ModelViewSet):
    permission_classes = [IsAuthenticated,IsWorkforce]
    serializer_class = ProjectSerializer
    def list(self, request, *args, **kwargs):
        user= request.user
        workspace_id= self.kwargs.get('workspace_pk')
        cache_key = f"project_list_user_{user.id}_workspace_{workspace_id}"

        cached= cache.get(cache_key)
        if cached:
            return Response(cached)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        response = self.get_paginated_response(serializer.data)
        cache.set(cache_key,response.data,timeout=60)

        return Response(response) 
    def get_queryset(self):
        return Projects.objects.filter(
        workspace__members=self.request.user
    ).select_related('workspace', 'created_by').annotate(
        task_count = Count('tasks',distinct=True),completed_tasks =Count(
            'tasks',filter=Q(tasks__status='done'),distinct=True
        )
    )
    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_pk')
        user =self.request.user
        membership  = Membership.objects.filter(
            user=user,workspace_id = workspace_id 
        ).first()

        if not membership or membership.role =='viewer':
            raise PermissionDenied('Viewers can\'t create Projects')

        serializer.save(
            workspace_id=workspace_id,
            created_by =self.request.user
        )
        
