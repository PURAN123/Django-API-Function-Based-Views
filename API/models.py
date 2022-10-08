from statistics import multimode
from rest_framework.authtoken.models import Token
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class User(AbstractUser):
  email = models.EmailField(max_length=50, unique=True, blank=False, null=False)
  phone = models.IntegerField(unique=True)
  dob = models.DateField()
  street = models.CharField(max_length=50)
  zipcode = models.IntegerField()
  city = models.CharField(max_length=50)
  state = models.CharField(max_length=50)
  country = models.CharField(max_length=50)
  password= models.CharField(max_length=200)

  
  def __str__(self) :
    return self.username
