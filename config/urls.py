

from django.contrib import admin
from django.urls import path,include
from projects.views import ProjectViewset
from workspaces.views import WorkspaceViewSet
from tasks.views import TaskViewset
from rest_framework_nested import routers
import debug_toolbar

router = routers.DefaultRouter()
router.register(r'workspaces',WorkspaceViewSet ,basename='workspace')

workspace_router = routers.NestedDefaultRouter(router,r'workspaces', lookup='workspace')
workspace_router.register(r'projects',ProjectViewset,basename='workspace-projects')

project_router  = routers.NestedDefaultRouter(workspace_router,r'projects',lookup='project')
project_router.register(r'tasks',TaskViewset,basename='project-tasks')
urlpatterns =router.urls+workspace_router.urls+project_router.urls
urlpatterns += [ 
     path('admin/', admin.site.urls),

     path ('accounts/' , include('allauth.urls')),
    path('api/auth/', include('accounts.urls'))
    ,path('__debug__/',include(debug_toolbar.urls))
    ]
#     path('',include('projects.urls')),

#     ,
#     path('api/workspaces/', include('workspaces.urls')),
# ]
