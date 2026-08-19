from rest_framework.pagination import CursorPagination, PageNumberPagination

class TaskCursorPagination(CursorPagination):
    page_size=10
    ordering='-created_at'

class WorkspacePagePagination(PageNumberPagination):
    page_size =10
