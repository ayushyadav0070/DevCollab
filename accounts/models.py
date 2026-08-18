from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager , PermissionsMixin

from django.utils import timezone
# Create your models here.


    
class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("Eamil required")
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('SuperUser must have is_staff = True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('SuperUser must have is_supperuser= True')

        return self.create_user(email,password,**extra_fields)
    

class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    github_id = models.CharField(unique=True, max_length=255,blank=True,null= True)
    avatar_url = models.URLField(blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    def __str__(self):
        return self.email
