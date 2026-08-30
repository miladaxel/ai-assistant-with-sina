from django.test import TestCase
from django.urls import reverse

from .models import Student, TeacherUser, Users


class StudentDetailViewAccessTests(TestCase):
    def setUp(self):
        self.teacher_user = Users.objects.create_user(
            username='teacher-one',
            password='test-pass',
            role='teacher',
        )
        self.teacher = TeacherUser.objects.create(
            user=self.teacher_user,
            subject='Math',
            first_name='Teacher',
            last_name='One',
        )
        self.other_teacher_user = Users.objects.create_user(
            username='teacher-two',
            password='test-pass',
            role='teacher',
        )
        self.other_teacher = TeacherUser.objects.create(
            user=self.other_teacher_user,
            subject='Science',
            first_name='Teacher',
            last_name='Two',
        )
        self.own_student = self.create_student('own-student', '001', '101')
        self.other_student = self.create_student('other-student', '002', '102')
        self.teacher.students.add(self.own_student)
        self.other_teacher.students.add(self.other_student)

    @staticmethod
    def create_student(username, national_code, id_card_number):
        user = Users.objects.create_user(
            username=username,
            password='test-pass',
            role='student',
        )
        return Student.objects.create(
            user=user,
            full_name=username,
            fathers_name='Father',
            national_code=national_code,
            id_card_number=id_card_number,
            birth_date='2000-01-01',
            birth_place='Tehran',
            home_phone_number='02100000000',
            transition='',
        )

    def test_teacher_can_view_own_student(self):
        self.client.force_login(self.teacher_user)

        response = self.client.get(
            reverse('student_detail', kwargs={'pk': self.own_student.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['student'], self.own_student)

    def test_teacher_cannot_view_another_teachers_student(self):
        self.client.force_login(self.teacher_user)

        response = self.client.get(
            reverse('student_detail', kwargs={'pk': self.other_student.pk})
        )

        self.assertEqual(response.status_code, 404)

    def test_student_is_forbidden(self):
        self.client.force_login(self.own_student.user)

        response = self.client.get(
            reverse('student_detail', kwargs={'pk': self.own_student.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse('student_detail', kwargs={'pk': self.own_student.pk})
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('student_detail', kwargs={'pk': self.own_student.pk})}",
        )
