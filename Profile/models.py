from django.contrib.auth.models import User
from django.db import models

class Student(models.Model):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    full_name = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=100)
    national_code = models.CharField(max_length=20, unique=True)
    id_card_number = models.CharField(max_length=20, unique=True)
    birth_date = models.CharField(max_length=20)
    birth_place = models.CharField(max_length=100)
    sex = models.CharField(max_length=1, choices=GENDER, default='M')
    clas = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    home_phone_number = models.CharField(max_length=20)
    transition = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.full_name