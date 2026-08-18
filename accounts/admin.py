from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('email', 'full_name','is_staff', 'is_active','github_id')
    list_filter = ('is_staff', 'is_active')

    ordering = ('email',)
    search_fields=('email','full_name')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'avatar_url')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('email',)

admin.site.register(User, CustomUserAdmin)