from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.core.validators import RegexValidator

persian_username_validator = RegexValidator(
        regex=r'^[0-9a-zA-z_\u0600-\u06FF\s]+$',
    )


class Users(AbstractUser):
    username = models.CharField(max_length=100, unique=True, validators=[persian_username_validator])

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('manager', 'Manager'),

    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=20, blank=True, null=True)


    def __str__(self):
        return self.username


class Student(models.Model):
    GENDER = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=100)
    national_code = models.CharField(max_length=20, unique=True)
    id_card_number = models.CharField(max_length=20, unique=True)
    birth_date = models.CharField(max_length=20)
    birth_place = models.CharField(max_length=100)
    sex = models.CharField(max_length=1, choices=GENDER, default='M')
    classes = models.ManyToManyField('SchoolClass', related_name='students', blank=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    home_phone_number = models.CharField(max_length=20)
    transition = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    teachers = models.ManyToManyField('TeacherUser', related_name='teachers',blank=True)
    # manager = models.ForeignKey('ManagerUser', on_delete=models.CASCADE, related_name='student_manager', blank=True, null=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.user:
            self.user.role = "student"

            self.user.save(update_fields=['role'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Student_information'
        verbose_name_plural = 'Students_information'


class TeacherUser(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='teacher_profile')

    subject = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    personal_code = models.CharField(max_length=20, unique=True,blank=True, null=True)
    national_code = models.CharField(max_length=20, unique=True,blank=True, null=True)
    education_level = models.CharField(max_length=100,blank=True, null=True)
    number_of_classes = models.IntegerField(blank=True, null=True)
    number_of_students = models.IntegerField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    students = models.ManyToManyField(Student, related_name='students', blank=True)
    # manager = models.ForeignKey('ManagerUser', on_delete=models.CASCADE, related_name='teacher_manager', blank=True, null=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


    def save(self, *args, **kwargs):
        if self.user:
            self.user.role = "teacher"

            self.user.save(update_fields=['role'])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'


class ManagerUser(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='manager_profile')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    personal_code = models.CharField(max_length=20, unique=True,blank=True, null=True)
    national_code = models.CharField(max_length=20, unique=True,blank=True, null=True)
    education_level = models.CharField(max_length=100,blank=True, null=True)
    # students = models.ManyToManyField('Student', related_name='students_manager', blank=True)
    # teachers = models.ManyToManyField('TeacherUser', related_name='teachers_manager', blank=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Manager'
        verbose_name_plural = 'Managers'


class SchoolClass(models.Model):
    number = models.PositiveIntegerField()
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(TeacherUser, on_delete=models.SET_NULL, related_name='classes', null=True, blank=True)

    def __str__(self):
        return f"کلاس {self.number}-{self.subject}"