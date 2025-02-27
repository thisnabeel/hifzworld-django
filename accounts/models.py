from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, default='null@email.com')
    password = models.CharField(max_length=128, default=make_password('default_password'))
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True)
    starting_verse_boundary = models.CharField(max_length=10, blank=True)  
    ending_verse_boundary = models.CharField(max_length=10, blank=True)    

    # **New Peer ID field for WebRTC**
    peer_id = models.CharField(max_length=255, unique=True, null=True, blank=True) 

    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"User {self.id}"

